"""
Multi-model forecasting implementations: Naive, Moving Average, Seasonal Naive, SARIMAX, and XGBoost.
"""
from typing import Dict, List, Tuple, Any
import numpy as np
import pandas as pd

try:
    from xgboost import XGBRegressor
    HAS_XGBOOST = True
except ImportError:
    XGBRegressor = None
    HAS_XGBOOST = False

try:
    from statsmodels.tsa.statespace.sarimax import SARIMAX
    HAS_SARIMAX = True
except ImportError:
    SARIMAX = None
    HAS_SARIMAX = False

from app.forecasting.evaluation import model_evaluator


class BaseForecastModel:
    def fit_predict(
        self, df_train: pd.DataFrame, df_future: pd.DataFrame
    ) -> Tuple[np.ndarray, Dict[str, float]]:
        raise NotImplementedError


class NaiveModel(BaseForecastModel):
    def fit_predict(
        self, df_train: pd.DataFrame, df_future: pd.DataFrame
    ) -> Tuple[np.ndarray, Dict[str, float]]:
        last_val = float(df_train["demand"].iloc[-1]) if not df_train.empty else 10.0
        preds = np.full(len(df_future), last_val)

        # In-sample validation metrics
        y_true = df_train["demand"].values[-len(df_future):] if len(df_train) >= len(df_future) else df_train["demand"].values
        y_pred = np.full(len(y_true), last_val)
        metrics = model_evaluator.evaluate(y_true, y_pred)
        return preds, metrics


class MovingAverageModel(BaseForecastModel):
    def __init__(self, window: int = 7):
        self.window = window

    def fit_predict(
        self, df_train: pd.DataFrame, df_future: pd.DataFrame
    ) -> Tuple[np.ndarray, Dict[str, float]]:
        ma_val = (
            float(df_train["demand"].tail(self.window).mean())
            if not df_train.empty
            else 10.0
        )
        preds = np.full(len(df_future), ma_val)

        y_true = df_train["demand"].values[-len(df_future):] if len(df_train) >= len(df_future) else df_train["demand"].values
        y_pred = np.full(len(y_true), ma_val)
        metrics = model_evaluator.evaluate(y_true, y_pred)
        return preds, metrics


class SeasonalNaiveModel(BaseForecastModel):
    def fit_predict(
        self, df_train: pd.DataFrame, df_future: pd.DataFrame
    ) -> Tuple[np.ndarray, Dict[str, float]]:
        # Same day of week mean demand
        dow_means = df_train.groupby("day_of_week")["demand"].mean().to_dict()
        default_mean = float(df_train["demand"].mean()) if not df_train.empty else 10.0

        preds = np.array([dow_means.get(row["day_of_week"], default_mean) for _, row in df_future.iterrows()])

        y_true = df_train["demand"].values[-len(df_future):] if len(df_train) >= len(df_future) else df_train["demand"].values
        y_pred = np.full(len(y_true), default_mean)
        metrics = model_evaluator.evaluate(y_true, y_pred)
        return preds, metrics


class SARIMAXModel(BaseForecastModel):
    def fit_predict(
        self, df_train: pd.DataFrame, df_future: pd.DataFrame
    ) -> Tuple[np.ndarray, Dict[str, float]]:
        if not HAS_SARIMAX or len(df_train) < 14:
            # Fallback to Moving Average if SARIMAX is missing or dataset is too small
            return MovingAverageModel().fit_predict(df_train, df_future)

        try:
            series = df_train["demand"].astype(float).values
            model = SARIMAX(series, order=(1, 1, 1), seasonal_order=(0, 0, 0, 0))
            res = model.fit(disp=False)
            preds = res.forecast(steps=len(df_future))

            y_true = series[-len(df_future):] if len(series) >= len(df_future) else series
            y_pred = res.fittedvalues[-len(y_true):]
            metrics = model_evaluator.evaluate(y_true, y_pred)
            return np.maximum(0, preds), metrics
        except Exception:
            return MovingAverageModel().fit_predict(df_train, df_future)


class XGBoostModel(BaseForecastModel):
    def fit_predict(
        self, df_train: pd.DataFrame, df_future: pd.DataFrame
    ) -> Tuple[np.ndarray, Dict[str, float]]:
        features = [
            "day_of_week",
            "month",
            "is_weekend",
            "lag_1",
            "lag_7",
            "rolling_7_mean",
            "rolling_14_mean",
            "holiday_flag",
            "event_importance",
        ]

        if not HAS_XGBOOST or len(df_train) < 14:
            return MovingAverageModel().fit_predict(df_train, df_future)

        try:
            X_train = df_train[features]
            y_train = df_train["demand"]

            model = XGBRegressor(
                n_estimators=50, max_depth=3, learning_rate=0.1, random_state=42
            )
            model.fit(X_train, y_train)

            X_future = df_future[features]
            preds = model.predict(X_future)

            in_sample_preds = model.predict(X_train)
            metrics = model_evaluator.evaluate(y_train.values, in_sample_preds)
            return np.maximum(0, preds), metrics
        except Exception:
            return MovingAverageModel().fit_predict(df_train, df_future)

