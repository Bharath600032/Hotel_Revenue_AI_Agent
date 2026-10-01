"""
Feature Engineering Store for Demand Forecasting Engine.
Generates lag features, calendar attributes, holiday/event indicators, and competitor pricing statistics.
"""
from datetime import date, timedelta
from typing import Dict, List, Tuple, Any
import numpy as np
import pandas as pd


class FeatureEngineer:
    """Engineers time-series features for hotel demand ML models."""

    @staticmethod
    def build_feature_dataframe(
        historical_records: List[Dict[str, Any]],
        future_dates: List[date],
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Build training and inference feature DataFrames from historical reservation/inventory records.
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

        # 3. External Signals (Default fillers if missing)
        if "holiday_flag" not in df_hist.columns:
            df_hist["holiday_flag"] = 0
        if "event_importance" not in df_hist.columns:
            df_hist["event_importance"] = 0
        if "competitor_median" not in df_hist.columns:
            df_hist["competitor_median"] = df_hist.get("adr", pd.Series([5000.0] * len(df_hist)))

        # Build Future Inference DataFrame
        future_rows = []
        last_demand = df_hist["demand"].iloc[-1] if not df_hist.empty else 10.0
        rolling_7 = df_hist["rolling_7_mean"].iloc[-1] if not df_hist.empty else 10.0

        for dt in future_dates:
            dt_ts = pd.to_datetime(dt)
            dow = dt_ts.dayofweek
            is_wknd = 1 if dow in [4, 5] else 0
            future_rows.append(
                {
                    "stay_date": dt_ts,
                    "day_of_week": dow,
                    "month": dt_ts.month,
                    "is_weekend": is_wknd,
                    "lag_1": last_demand,
                    "lag_7": rolling_7,
                    "rolling_7_mean": rolling_7,
                    "rolling_14_mean": rolling_7,
                    "holiday_flag": 0,
                    "event_importance": 0,
                    "competitor_median": 5500.0,
                }
            )

        df_future = pd.DataFrame(future_rows)
        return df_hist, df_future


feature_engineer = FeatureEngineer()
