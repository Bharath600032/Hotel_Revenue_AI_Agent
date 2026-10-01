import React, { useState } from 'react';
import { apiService } from '../services/api';
import { RAGSearchResult } from '../types';
import { useHotel } from '../context/HotelContext';
import {
  BookOpen,
  Search,
  Upload,
  Globe,
  Link2,
  CheckCircle2,
  Building2,
  RotateCw,
  Sparkles,
  ExternalLink,
  Layers,
} from 'lucide-react';
import { ProvisioningPercentageLoader } from '../components/ProvisioningPercentageLoader';

export const RAG: React.FC = () => {
  const { selectedHotel } = useHotel();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<RAGSearchResult[]>([]);
  const [searching, setSearching] = useState(false);

  // Document Upload State
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState('Revenue Management SOP');
  const [content, setContent] = useState('');
  const [uploading, setUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState('');

  // Website Link Crawl State
  const [websiteUrl, setWebsiteUrl] = useState('');
  const [maxSublinks, setMaxSublinks] = useState(8);
  const [crawling, setCrawling] = useState(false);
  const [crawlProgress, setCrawlProgress] = useState(0);
  const [crawlStep, setCrawlStep] = useState('');
  const [crawlTimer, setCrawlTimer] = useState(0);
  const [crawlResult, setCrawlResult] = useState<any>(null);
  const [crawlError, setCrawlError] = useState('');

  const activeHotelId = selectedHotel?.hotel_id;

  // Restore RAG crawl state & website URL per hotel across tab switches
  React.useEffect(() => {
    if (!activeHotelId) return;
    const savedUrl = sessionStorage.getItem(`rag_website_url_${activeHotelId}`);
    const savedResult = sessionStorage.getItem(`rag_crawl_result_${activeHotelId}`);

    if (savedUrl) setWebsiteUrl(savedUrl);
    if (savedResult) {
      try {
        setCrawlResult(JSON.parse(savedResult));
      } catch (e) {
        console.error('Failed to parse saved crawl result:', e);
      }
    }
  }, [activeHotelId]);

  // Persist crawl result whenever updated
  React.useEffect(() => {
    if (activeHotelId && crawlResult) {
      sessionStorage.setItem(`rag_crawl_result_${activeHotelId}`, JSON.stringify(crawlResult));
      if (websiteUrl) {
        sessionStorage.setItem(`rag_website_url_${activeHotelId}`, websiteUrl);
      }
    }
  }, [crawlResult, websiteUrl, activeHotelId]);

  // Live timer interval while crawling
  React.useEffect(() => {
    let timer: any = null;
    if (crawling) {
      setCrawlTimer(0);
      timer = setInterval(() => {
        setCrawlTimer((prev) => prev + 1);
      }, 1000);
    }
    return () => {
      if (timer) clearInterval(timer);
    };
  }, [crawling]);

  const formatTimer = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}s`;
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    try {
      setSearching(true);
      const res = await apiService.searchRAG(query, activeHotelId);
      setResults(res.results || []);
    } catch (err) {
      console.error('Failed to execute RAG search:', err);
    } finally {
      setSearching(false);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title || !content) return;
    try {
      setUploading(true);
      const res = await apiService.uploadRAGDocument(title, category, content, activeHotelId);
      setUploadSuccess(`Document vectorized for ${selectedHotel?.hotel_name || 'hotel'}! Created ${res.chunks_created} vector chunk(s).`);
      setTitle('');
      setContent('');
    } catch (err) {
      console.error('Failed to ingest document:', err);
    } finally {
      setUploading(false);
    }
  };

  const handleCrawlWebsite = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!websiteUrl.trim()) return;
    let progressInterval: any = null;
    setCrawlError('');

    try {
      setCrawling(true);
      setCrawlProgress(5);
      setCrawlStep(`Connecting to official website ${websiteUrl}...`);

      let currentPct = 5;
      progressInterval = setInterval(() => {
        currentPct += Math.floor(Math.random() * 3) + 2;
        if (currentPct > 92) currentPct = 92;
        setCrawlProgress(currentPct);

        if (currentPct < 25) {
          setCrawlStep(`Connecting & Fetching HTML Landing Page from ${websiteUrl}...`);
        } else if (currentPct < 55) {
          setCrawlStep('Discovering internal sublinks (/rooms, /dining, /offers, /amenities)...');
        } else if (currentPct < 80) {
          setCrawlStep('Parsing room categories, descriptions & textual content...');
        } else {
          setCrawlStep('Generating sentence embeddings & indexing vector chunks into ChromaDB...');
        }
      }, 90);

      const res = await apiService.scrapeRAGWebsite(websiteUrl.trim(), activeHotelId, maxSublinks);

      if (progressInterval) clearInterval(progressInterval);
      setCrawlProgress(100);
      setCrawlStep('Website & Sublinks Vectorized into ChromaDB Knowledge Base!');
      setCrawlResult(res);

      setTimeout(() => {
        setCrawling(false);
        setCrawlProgress(0);
      }, 500);
    } catch (err: any) {
      if (progressInterval) clearInterval(progressInterval);
      console.error('Failed to crawl hotel website:', err);
      setCrawlError('Failed to fetch website. Make sure the URL is accessible (e.g. https://cuteorange.in).');
      setCrawling(false);
      setCrawlProgress(0);
    }
  };


  return (
    <div className="space-y-8 font-sans">
      {/* Page Header Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-white flex items-center gap-3">
            <div className="p-2.5 bg-gradient-to-tr from-indigo-600 to-purple-600 rounded-2xl shadow-lg shadow-indigo-600/30">
              <BookOpen className="w-6 h-6 text-white" />
            </div>
            RAG Knowledge Base & Hotel Web Scraper
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Vectorized strategy documents, policy SOPs, and official hotel website sublink crawling for grounded AI reasoning.
          </p>
        </div>

        {/* Active Property Scope Pill */}
        {selectedHotel && (
          <div className="px-4 py-2 bg-slate-900 border border-slate-800 rounded-2xl flex items-center gap-2.5 text-xs font-bold text-slate-200 shadow-md">
            <Building2 className="w-4 h-4 text-indigo-400" />
            <div>
              <span className="text-[10px] text-slate-400 block font-mono">ACTIVE HOTEL SCOPE</span>
              <span className="text-white font-extrabold">{selectedHotel.hotel_name}</span>
            </div>
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse ml-1" />
          </div>
        )}
      </div>

      {/* WEB SCRAER & SUBLINK CRAWLER ATTACHMENT */}
      <div className="p-6 bg-slate-900/90 border border-slate-800 rounded-3xl space-y-6 shadow-2xl backdrop-blur relative overflow-hidden">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-4">
          <div>
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Globe className="w-5 h-5 text-indigo-400" />
              Official Hotel Website Attachment & Deep Sublink Vector Crawler
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Provide the hotel's official website URL. The AI automatically crawls the landing page + all internal sublinks (/rooms, /dining, /offers, /amenities) and stores them in vector DB for instant RAG search!
            </p>
          </div>
          <span className="px-3 py-1 bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-xs font-mono font-bold rounded-full self-start md:self-auto">
            AUTOMATIC SUBLINK DISCOVERY
          </span>
        </div>

        {crawling ? (
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-slate-950/80 border border-indigo-500/30 rounded-2xl">
              <span className="text-xs font-mono font-bold text-indigo-300 flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-indigo-400 animate-ping" />
                CHROMADB VECTOR INGESTION ACTIVE
              </span>
              <span className="text-xs font-mono font-extrabold text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-full border border-emerald-500/20">
                ⏱️ Elapsed: {formatTimer(crawlTimer)}
              </span>
            </div>
            <ProvisioningPercentageLoader
              progress={crawlProgress}
              currentStep={crawlStep}
              title="Crawling Official Hotel Website & Deep Sublinks..."
              subtitle={`Chunking text & generating sentence embeddings into ChromaDB vector store for ${websiteUrl}...`}
              steps={[
                { label: `Connecting to domain ${websiteUrl}`, minProgress: 20 },
                { label: "Fetching HTML landing page & parsing meta tags", minProgress: 40 },
                { label: "Discovering internal sublinks (/rooms, /dining, /offers)", minProgress: 65 },
                { label: "Parsing room categories & textual content", minProgress: 85 },
                { label: "Indexing sentence embeddings into ChromaDB Knowledge Base", minProgress: 100 }
              ]}
            />
          </div>
        ) : (
          <form onSubmit={handleCrawlWebsite} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="md:col-span-2">
                <label className="text-xs font-bold text-slate-300 flex items-center gap-1.5 mb-1.5">
                  <Link2 className="w-3.5 h-3.5 text-indigo-400" />
                  Official Hotel Website URL
                </label>
                <input
                  type="text"
                  value={websiteUrl}
                  onChange={(e) => setWebsiteUrl(e.target.value)}
                  placeholder={`e.g. https://cuteorange.in or https://${selectedHotel?.hotel_name.toLowerCase().replace(/\s+/g, '')}.com`}
                  className="w-full bg-slate-950 border border-slate-800 text-white text-xs p-3 rounded-2xl focus:border-indigo-500 outline-none font-mono"
                  required
                />
              </div>

              <div>
                <label className="text-xs font-bold text-slate-300 flex items-center gap-1.5 mb-1.5">
                  <Layers className="w-3.5 h-3.5 text-purple-400" />
                  Max Sublinks Depth
                </label>
                <select
                  value={maxSublinks}
                  onChange={(e) => setMaxSublinks(Number(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-800 text-white text-xs p-3 rounded-2xl focus:border-indigo-500 outline-none"
                >
                  <option value={5}>5 Sublinks (Fast Crawl)</option>
                  <option value={8}>8 Sublinks (Recommended)</option>
                  <option value={15}>15 Sublinks (Deep Crawl)</option>
                </select>
              </div>
            </div>

            <button
              type="submit"
              disabled={crawling}
              className="px-6 py-3.5 bg-gradient-to-r from-indigo-600 via-purple-600 to-emerald-600 hover:from-indigo-500 hover:to-emerald-500 text-white text-xs font-extrabold rounded-2xl shadow-xl shadow-indigo-600/30 flex items-center justify-center gap-2 transition-all hover:scale-[1.01]"
            >
              <Globe className="w-4 h-4" />
              Attach Website & Crawl All Sublinks into Vector DB
            </button>
          </form>
        )}

        {crawlError && (
          <div className="p-4 bg-rose-500/10 border border-rose-500/30 rounded-2xl text-rose-400 text-xs font-bold">
            ⚠️ {crawlError}
          </div>
        )}

        {crawlResult && (
          <div className="p-5 bg-slate-950/90 border border-indigo-500/30 rounded-2xl space-y-4 animate-fadeIn">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <span className="text-xs font-bold text-emerald-400 flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4" />
                Successfully Crawled & Indexed {crawlResult.pages_crawled_count} Page(s)!
              </span>
              <span className="text-xs font-mono font-bold text-indigo-300 bg-indigo-500/20 px-3 py-1 rounded-full border border-indigo-500/30">
                {crawlResult.total_chunks_indexed} Vector Chunks Stored in ChromaDB
              </span>
            </div>

            {/* Extracted Room Categories Pill Box */}
            {crawlResult.discovered_room_types && crawlResult.discovered_room_types.length > 0 && (
              <div className="p-3 bg-indigo-950/30 border border-indigo-500/20 rounded-xl space-y-1.5">
                <span className="text-[11px] font-bold text-indigo-300 uppercase font-mono tracking-wider block">
                  🏨 Discovered Room Categories Parsed From Website:
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {crawlResult.discovered_room_types.map((roomName: string, rIdx: number) => (
                    <span key={rIdx} className="px-2.5 py-1 bg-indigo-600/20 text-indigo-200 border border-indigo-500/40 text-xs font-semibold rounded-lg">
                      ✨ {roomName}
                    </span>
                  ))}
                </div>
              </div>
            )}

            <div className="space-y-2 text-xs">
              <p className="text-slate-400 text-[11px] font-mono uppercase tracking-wider">Indexed Pages & Internal Sublinks:</p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 max-h-48 overflow-y-auto pr-1">
                {crawlResult.pages?.map((p: any, idx: number) => (
                  <div key={idx} className="p-2.5 bg-slate-900 border border-slate-800 rounded-xl flex items-center justify-between">
                    <div className="truncate mr-2">
                      <span className="text-white font-bold block truncate">{p.title}</span>
                      <a href={p.url} target="_blank" rel="noreferrer" className="text-[10px] text-indigo-400 flex items-center gap-1 hover:underline truncate">
                        {p.url} <ExternalLink className="w-2.5 h-2.5 inline" />
                      </a>
                    </div>
                    <span className="text-[10px] font-mono font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded shrink-0">
                      {p.chunks_created} vectors
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Semantic Vector Search Tester */}
        <div className="p-6 bg-slate-900 border border-slate-800 rounded-3xl space-y-4 shadow-2xl">
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <Search className="w-5 h-5 text-indigo-400" />
            Semantic Similarity Search Tester
          </h3>
          <p className="text-xs text-slate-400">
            Searches across strategy documents + crawled website sublinks for <strong className="text-white">{selectedHotel?.hotel_name}</strong>.
          </p>

          <form onSubmit={handleSearch} className="flex gap-2">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSearch(e);
                }
              }}
              placeholder="e.g. What rooms or dining options are offered at the hotel?"
              className="flex-1 bg-slate-950 border border-slate-800 text-white text-xs p-3 rounded-2xl focus:border-indigo-500 outline-none"
            />
            <button
              type="submit"
              disabled={searching}
              className="px-5 py-3 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold rounded-2xl shadow-lg shadow-indigo-600/30 shrink-0"
            >
              {searching ? <RotateCw className="w-4 h-4 animate-spin" /> : 'Search'}
            </button>
          </form>

          {searching ? (
            <div className="flex justify-center items-center h-36">
              <div className="animate-spin rounded-full h-7 w-7 border-b-2 border-indigo-500"></div>
            </div>
          ) : results.length > 0 ? (
            <div className="space-y-3 max-h-96 overflow-y-auto pr-1">
              {results.map((r, i) => (
                <div key={i} className="p-4 bg-slate-950/90 border border-slate-800 rounded-2xl space-y-1.5 shadow-md">
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-bold text-indigo-300">{r.title}</span>
                    <span className="text-emerald-400 font-mono text-[10px] bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                      Match Score: {(r.similarity_score * 100).toFixed(1)}%
                    </span>
                  </div>
                  <p className="text-xs text-slate-300 leading-relaxed">{r.content}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-slate-500 text-center py-8">Enter a natural language search query above.</p>
          )}
        </div>

        {/* Upload Strategy Document / SOP */}
        <div className="p-6 bg-slate-900 border border-slate-800 rounded-3xl space-y-4 shadow-2xl">
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <Upload className="w-5 h-5 text-emerald-400" />
            Ingest Strategy Document / SOP Policy
          </h3>
          <p className="text-xs text-slate-400">
            Upload text policy documents specifically assigned to <strong className="text-white">{selectedHotel?.hotel_name}</strong>.
          </p>

          <form onSubmit={handleUpload} className="space-y-3 text-xs">
            <div>
              <label className="text-slate-300 font-bold">Document Title</label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. Peak Season Minimum Stay SOP"
                className="w-full bg-slate-950 border border-slate-800 text-white p-3 rounded-2xl mt-1"
                required
              />
            </div>

            <div>
              <label className="text-slate-300 font-bold">Category</label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 text-white p-3 rounded-2xl mt-1"
              >
                <option value="Revenue Management SOP">Revenue Management SOP</option>
                <option value="Corporate Contract">Corporate Contract Rate Plan</option>
                <option value="Cancellation Policy">Cancellation & Refund Policy</option>
                <option value="Competitor Strategy">Competitor Positioning Strategy</option>
              </select>
            </div>

            <div>
              <label className="text-slate-300 font-bold">Document Content Text</label>
              <textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="Paste full text policy body here..."
                className="w-full bg-slate-950 border border-slate-800 text-white p-3 rounded-2xl h-28 mt-1"
                required
              />
            </div>

            <button
              type="submit"
              disabled={uploading}
              className="w-full py-3 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-bold rounded-2xl shadow-lg shadow-emerald-600/20 flex items-center justify-center gap-2"
            >
              <Sparkles className="w-4 h-4" />
              {uploading ? 'Vectorizing Document...' : 'Ingest Document into Vector Store'}
            </button>
          </form>

          {uploadSuccess && (
            <div className="p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-2xl text-emerald-400 text-xs font-bold flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4" />
              {uploadSuccess}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
