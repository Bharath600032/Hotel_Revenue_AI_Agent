"""
Hotel Website Scraper & Sublink Crawler Service for RAG Knowledge Base.
Crawls a hotel's official website URL, extracts textual content from main page and internal sublinks,
and ingests vectors into the RAG Knowledge Base.
"""
import urllib.request
import urllib.parse
from html.parser import HTMLParser
import re
from typing import List, Dict, Set, Optional, Tuple, Any
from app.rag.vector_store import vector_store_manager
from app.core.logging import get_logger


logger = get_logger("app.rag.website_scraper")


class SimpleHTMLTextExtractor(HTMLParser):
    """
    Parser to extract text content and internal links from HTML documents.
    """
    def __init__(self, base_url: str):
        super().__init__()
        self.base_url = base_url
        self.base_domain = urllib.parse.urlparse(base_url).netloc
        self.text_parts: List[str] = []
        self.title: str = ""
        self.in_title: bool = False
        self.links: Set[str] = set()
        self.ignore_tags = {'script', 'style', 'head', 'meta', 'link', 'svg', 'noscript'}
        self.current_tag: Optional[str] = None

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]):
        tag_lower = tag.lower()
        self.current_tag = tag_lower
        if tag_lower == 'title':
            self.in_title = True

        if tag_lower == 'a':
            for attr_name, attr_val in attrs:
                if attr_name == 'href' and attr_val:
                    # Resolve relative URLs
                    full_url = urllib.parse.urljoin(self.base_url, attr_val)
                    # Strip fragment anchors (#section)
                    full_url = full_url.split('#')[0].rstrip('/')
                    parsed = urllib.parse.urlparse(full_url)
                    # Stay on same domain and HTTP/HTTPS
                    if parsed.scheme in ('http', 'https') and parsed.netloc == self.base_domain:
                        # Avoid non-HTML assets (pdf, jpg, png, etc.)
                        if not re.search(r'\.(pdf|jpg|jpeg|png|gif|svg|css|js|zip|mp4)$', parsed.path.lower()):
                            self.links.add(full_url)

    def handle_endtag(self, tag: str):
        if tag.lower() == 'title':
            self.in_title = False
        self.current_tag = None

    def handle_data(self, data: str):
        cleaned = data.strip()
        if not cleaned:
            return

        if self.in_title:
            self.title += " " + cleaned
        elif self.current_tag not in self.ignore_tags:
            self.text_parts.append(cleaned)

    def get_clean_text(self) -> str:
        return " ".join(self.text_parts)


class WebsiteScraperService:
    """
    Service for crawling hotel websites and sublinks, converting pages to RAG vectors.
    """

    @staticmethod
    def fetch_and_parse(url: str) -> Tuple[str, str, Set[str]]:
        """
        Fetch HTML from URL, return (title, text_content, internal_links).
        """
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) HotelRevenueAIBot/1.0"
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=8) as response:
                content_type = response.headers.get("Content-Type", "")
                if "text/html" not in content_type and "application/xhtml" not in content_type:
                    return ("", "", set())
                html_bytes = response.read()
                html_text = html_bytes.decode("utf-8", errors="ignore")

            parser = SimpleHTMLTextExtractor(url)
            parser.feed(html_text)

            title = parser.title.strip() or urllib.parse.urlparse(url).path or url
            clean_text = parser.get_clean_text()
            return (title, clean_text, parser.links)
        except Exception as e:
            logger.warning("failed_to_scrape_url", url=url, error=str(e))
            return ("", "", set())

    def extract_discovered_room_types(self, pages: List[Tuple[str, str]]) -> List[str]:
        """
        Extract unique room names & category titles from scraped HTML page titles and text content.
        """
        discovered = set()
        pattern = re.compile(
            r'\b(?:Deluxe|Superior|Executive|Standard|Luxury|Presidential|Junior|Ocean|City|Garden|Family|King|Twin|Club|Royal|Grand|Penthouse|Beach|Premier|Classic|Comfort|Suite|Villa)\b[^\.\n,:;!?]*?\b(?:Room|Rooms|Suite|Suites|Villa|Villas|Studio|Bungalow|Penthouse|Apartment)\b',
            re.IGNORECASE
        )

        for title, text in pages:
            # Check title first
            for match in pattern.findall(title):
                cleaned = re.sub(r'\s+', ' ', match).strip().title()
                if 5 <= len(cleaned) <= 45:
                    discovered.add(cleaned)

            # Check text
            for match in pattern.findall(text):
                cleaned = re.sub(r'\s+', ' ', match).strip().title()
                if 5 <= len(cleaned) <= 45:
                    discovered.add(cleaned)

        return list(discovered)

    def crawl_and_ingest_website(
        self,
        url: str,
        hotel_id: Optional[int] = None,
        max_sublinks: int = 8,
        db: Optional[Any] = None,
    ) -> Dict:
        """
        Crawl main website URL + discovered internal sublinks up to max_sublinks,
        extract text, ingest into RAG Knowledge Base, and sync room categories to DB.
        """
        # Normalize target URL
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url

        visited_urls: Set[str] = set()
        crawled_pages: List[Dict] = []
        raw_pages_data: List[Tuple[str, str]] = []
        total_chunks = 0

        # Step 1: Scrape Main Landing Page
        main_title, main_text, sublinks = self.fetch_and_parse(url)
        visited_urls.add(url.rstrip('/'))

        if main_text:
            raw_pages_data.append((main_title, main_text))
            chunk_ids = vector_store_manager.ingest_document(
                title=f"🌐 Website: {main_title}",
                category="Hotel Website",
                content=f"Official Hotel Website Main Page ({url}):\n{main_text}",
                hotel_id=hotel_id,
                version="Scraped Live",
            )
            crawled_pages.append({
                "url": url,
                "title": main_title,
                "chunks_created": len(chunk_ids),
                "is_main_page": True
            })
            total_chunks += len(chunk_ids)

        # Step 2: Crawl Discovered Internal Sublinks (Rooms, Dining, Offers, Amenities, etc.)
        sublinks_to_crawl = [link for link in sublinks if link.rstrip('/') not in visited_urls][:max_sublinks]

        for link_url in sublinks_to_crawl:
            normalized_link = link_url.rstrip('/')
            if normalized_link in visited_urls:
                continue
            visited_urls.add(normalized_link)

            sub_title, sub_text, _ = self.fetch_and_parse(link_url)
            if sub_text and len(sub_text) > 100:
                raw_pages_data.append((sub_title, sub_text))
                chunk_ids = vector_store_manager.ingest_document(
                    title=f"🔗 Sublink: {sub_title}",
                    category="Hotel Website Sublink",
                    content=f"Hotel Website Page ({link_url}):\n{sub_text}",
                    hotel_id=hotel_id,
                    version="Crawled Sublink",
                )
                crawled_pages.append({
                    "url": link_url,
                    "title": sub_title,
                    "chunks_created": len(chunk_ids),
                    "is_main_page": False
                })
                total_chunks += len(chunk_ids)

        # Step 3: Extract Room Types & Sync with SQL DB if db session & hotel_id are provided
        extracted_rooms = self.extract_discovered_room_types(raw_pages_data)

        if db and hotel_id and extracted_rooms:
            try:
                from app.models.hotel import RoomType, Hotel
                hotel_obj = db.query(Hotel).filter(Hotel.hotel_id == hotel_id).first()
                h_code = hotel_obj.hotel_code if hotel_obj else "HTL"

                existing_rts = db.query(RoomType).filter(RoomType.hotel_id == hotel_id).all()
                existing_names = {rt.room_type_name.lower(): rt for rt in existing_rts}

                for idx, r_name in enumerate(extracted_rooms[:5]):
                    if r_name.lower() not in existing_names:
                        code_suffix = "".join([w[0].upper() for w in r_name.split() if w])[:4]
                        new_rt = RoomType(
                            hotel_id=hotel_id,
                            room_type_code=f"{h_code}_{code_suffix}_{idx+1}",
                            room_type_name=r_name,
                            base_price=round((hotel_obj.min_price_floor if hotel_obj else 4000) * (1.2 + idx * 0.3), 0),
                            total_inventory=10,
                            max_occupancy=2,
                        )
                        db.add(new_rt)
                db.commit()
                logger.info("synced_website_room_types_to_db", hotel_id=hotel_id, rooms=extracted_rooms)
            except Exception as err:
                logger.warning("failed_to_sync_scraped_rooms_to_db", error=str(err))

        logger.info(
            "website_crawling_completed",
            target_url=url,
            pages_crawled=len(crawled_pages),
            total_chunks=total_chunks,
            discovered_rooms=extracted_rooms,
        )

        return {
            "target_url": url,
            "hotel_id": hotel_id,
            "pages_crawled_count": len(crawled_pages),
            "total_chunks_indexed": total_chunks,
            "discovered_room_types": extracted_rooms,
            "pages": crawled_pages,
        }


website_scraper_service = WebsiteScraperService()

