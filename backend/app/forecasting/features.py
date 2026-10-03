"""
Feature Engineering Store for Demand Forecasting Engine.
Generates lag features, calendar attributes, holiday/event indicators, and competitor pricing statistics.
"""
from datetime import date, timedelta
from typing import Dict, List, Tuple, Any, Optional
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session


class FeatureEngineer:
    """Engineers time-series features for hotel demand ML models."""

    @staticmethod
    def build_feature_dataframe(
        historical_records: List[Dict[str, Any]],
        future_dates: List[date],
        db: Optional[Session] = None,
        hotel_id: Optional[int] = None,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Build training and inference feature DataFrames from historical reservation/inventory records
        and live database signals (events, holidays, comp-set median rates).
        """
        if not historical_records:
            return pd.DataFrame(), pd.DataFrame()

        df_hist = pd.DataFrame(historical_records)
        df_hist["stay_date"] = pd.to_datetime(df_hist["stay_date"])
        df_hist = df_hist.sort_values("stay_date").reset_index(drop=True)

        # 1. Calendar Features
        df_hist["day_of_week"] = df_hist["stay_date"].dt.dayofweek
        df_hist["month"] = df_hist["stay_date"].dt.month
        df_hist["is_weekend"] = df_hist["day_of_week"].isin([4, 5]).astype(int)

        # 2. Demand Lags & Rolling Means
        df_hist["lag_1"] = df_hist["demand"].shift(1).fillna(df_hist["demand"].mean())
        df_hist["lag_7"] = df_hist["demand"].shift(7).fillna(df_hist["demand"].mean())
        df_hist["rolling_7_mean"] = df_hist["demand"].shift(1).rolling(7, min_periods=1).mean().fillna(df_hist["demand"].mean())
        df_hist["rolling_14_mean"] = df_hist["demand"].shift(1).rolling(14, min_periods=1).mean().fillna(df_hist["demand"].mean())

        # Look up Hotel details for city matching
        hotel_city = None
        if db and hotel_id:
            from app.models import Hotel
            h_obj = db.query(Hotel).filter(Hotel.hotel_id == hotel_id).first()
            if h_obj:
                hotel_city = h_obj.city

        # Helper to query DB signals for a date
        def get_date_signals(target_date: date) -> Tuple[int, int, float]:
            h_flag = 0
            ev_imp = 0
            comp_med = 5500.0

            if not db:
                return h_flag, ev_imp, comp_med

            try:
                from app.models import Holidays, Events, CompetitorRates, CompetitorHotels

                # Holiday Signal
                h_count = db.query(Holidays).filter(Holidays.holiday_date == target_date).count()
                if h_count > 0:
                    h_flag = 1

                # Event Signal
                if hotel_city:
                    ev = (
                        db.query(Events)
                        .filter(
                            Events.city.ilike(f"%{hotel_city}%"),
                            Events.start_date <= target_date,
                            Events.end_date >= target_date,
                        )
                        .order_by(Events.importance.desc())
                        .first()
                    )
                    if ev:
                        ev_imp = ev.importance

                # Competitor Median Signal
                if hotel_id:
                    c_rates = (
                        db.query(CompetitorRates.rate)
                        .join(CompetitorHotels, CompetitorRates.competitor_id == CompetitorHotels.competitor_id)
                        .filter(CompetitorHotels.hotel_id == hotel_id, CompetitorRates.stay_date == target_date)
                        .all()
                    )
                    if c_rates:
                        comp_med = float(np.median([r[0] for r in c_rates]))
            except Exception:
                pass

            return h_flag, ev_imp, comp_med

        # 3. External Signals for Historical DataFrame
        if "holiday_flag" not in df_hist.columns or "event_importance" not in df_hist.columns or "competitor_median" not in df_hist.columns:
            h_flags, ev_imps, comp_meds = [], [], []
            for _, row in df_hist.iterrows():
                dt_val = row["stay_date"].date() if hasattr(row["stay_date"], "date") else row["stay_date"]
                hf, ei, cm = get_date_signals(dt_val)
                h_flags.append(hf)
                ev_imps.append(ei)
                comp_meds.append(cm)
            
            df_hist["holiday_flag"] = h_flags
            df_hist["event_importance"] = ev_imps
            df_hist["competitor_median"] = comp_meds

        # 4. Build Future Inference DataFrame with Dynamic Day-of-Week Lags & Live Signals
        future_rows = []
        last_demand = df_hist["demand"].iloc[-1] if not df_hist.empty else 10.0
        rolling_7 = df_hist["rolling_7_mean"].iloc[-1] if not df_hist.empty else 10.0

        for dt in future_dates:
            dt_ts = pd.to_datetime(dt)
            dow = dt_ts.dayofweek
            is_wknd = 1 if dow in [4, 5] else 0

            hf, ei, cm = get_date_signals(dt)

            # Day-of-week multiplier for realistic feature propagation
            dow_mult = 1.30 if is_wknd else (1.10 if dow in [2, 3] else (0.75 if dow == 6 else 0.90))
            if ei > 0:
                dow_mult += 0.25
            if hf > 0:
                dow_mult += 0.20

            lag_val = round(rolling_7 * dow_mult, 1)

            future_rows.append(
                {
                    "stay_date": dt_ts,
                    "day_of_week": dow,
                    "month": dt_ts.month,
                    "is_weekend": is_wknd,
                    "lag_1": lag_val,
                    "lag_7": lag_val,
                    "rolling_7_mean": rolling_7,
                    "rolling_14_mean": rolling_7,
                    "holiday_flag": hf,
                    "event_importance": ei,
                    "competitor_median": cm,
                }
            )

        df_future = pd.DataFrame(future_rows)
        return df_hist, df_future


feature_engineer = FeatureEngineer()
