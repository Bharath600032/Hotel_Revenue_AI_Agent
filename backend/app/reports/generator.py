"""
Excel (.xlsx) and CSV Report Generator using openpyxl and pandas.
Generates 365-day pricing recommendations, demand forecasts, and competitor rate reports.
"""
import io
import pandas as pd
from datetime import date
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows

from app.models import PriceRecommendations, Forecasts, CompetitorRates, Hotel, RoomType


class ReportGenerator:
    """Generates styled Excel spreadsheets and CSV exports for hotel revenue managers."""

    @staticmethod
    def style_workbook(wb: Workbook) -> Workbook:
        """Apply executive styling, font colors, and number formatting to workbook."""
        header_fill = PatternFill(start_color="1E1B4B", end_color="1E1B4B", fill_type="solid")
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        border_side = Side(style="thin", color="CBD5E1")
        border = Border(left=border_side, right=border_side, top=border_side, bottom=border_side)

        for ws in wb.worksheets:
            ws.views.sheetView[0].showGridLines = True
            for col in ws.columns:
                max_len = max(len(str(cell.value or '')) for cell in col)
                col_letter = col[0].column_letter
                ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

            for row in ws.iter_rows(min_row=1, max_row=1):
                for cell in row:
                    cell.fill = header_fill
                    cell.font = header_font
                    cell.alignment = Alignment(horizontal="center", vertical="center")

            for row in ws.iter_rows(min_row=2):
                for cell in row:
                    cell.border = border

        return wb

    def generate_pricing_recommendations_excel(
        self, db: Session, hotel_id: int, start_date: date, end_date: date
    ) -> bytes:
        """Generate styled 365-day rate recommendation Excel spreadsheet."""
        recs = (
            db.query(PriceRecommendations)
            .filter(
                PriceRecommendations.hotel_id == hotel_id,
                PriceRecommendations.stay_date >= start_date,
                PriceRecommendations.stay_date <= end_date,
            )
            .order_by(PriceRecommendations.stay_date)
            .all()
        )

        rows = []
        for r in recs:
            rows.append(
                {
                    "Stay Date": str(r.stay_date),
                    "Room Type ID": r.room_type_id,
                    "Current Base Rate (₹)": r.current_rate,
                    "Recommended Rate (₹)": r.recommended_rate,
                    "Min Safe Rate (₹)": r.min_rate,
                    "Max Safe Rate (₹)": r.max_rate,
                    "Occupancy (%)": r.occupancy,
                    "Forecast Demand": r.forecast_demand,
                    "Competitor Median (₹)": r.competitor_median,
                    "Demand Index": r.demand_index,
                    "Approval Required": "YES" if r.requires_approval else "NO",
                    "Status": r.status,
                    "Reasoning & Signals": r.price_reason,
                }
            )

        if not rows:
            # Add header row placeholder if empty
            rows.append({"Stay Date": str(start_date), "Status": "No recommendations generated"})

        df = pd.DataFrame(rows)
        wb = Workbook()
        ws = wb.active
        ws.title = "Pricing Recommendations"

        for r in dataframe_to_rows(df, index=False, header=True):
            ws.append(r)

        wb = self.style_workbook(wb)
        output = io.BytesIO()
        wb.save(output)
        return output.getvalue()


report_generator = ReportGenerator()
