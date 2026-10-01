"""
Model Evaluation Framework & Time-Series Cross-Validation.
Computes MAE, RMSE, MAPE, WAPE, and executes winning model selection.
"""
from typing import Dict, List, Tuple
import numpy as np


class ModelEvaluator:
    """Evaluates time-series model forecast performance avoiding data leakage."""

    @staticmethod
    def calculate_mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        return float(np.mean(np.abs(y_true - y_pred)))

    @staticmethod
    def calculate_rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))

    @staticmethod
    def calculate_mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        mask = y_true != 0
        if not np.any(mask):
            return 0.0
        return float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100.0)

    @staticmethod
    def calculate_wape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        sum_true = np.sum(np.abs(y_true))
        if sum_true == 0:
            return 0.0
        return float((np.sum(np.abs(y_true - y_pred)) / sum_true) * 100.0)

    @classmethod
    def evaluate(cls, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """Compute all 4 evaluation metrics for a model predictions array."""
        return {
            "mae": round(cls.calculate_mae(y_true, y_pred), 2),
            "rmse": round(cls.calculate_rmse(y_true, y_pred), 2),
            "mape": round(cls.calculate_mape(y_true, y_pred), 2),
            "wape": round(cls.calculate_wape(y_true, y_pred), 2),
        }

    @classmethod
    def select_best_model(cls, model_results: Dict[str, Dict[str, float]]) -> str:
        """
        Select winning model name based on lowest WAPE / MAE metric score.
        """
        if not model_results:
            return "MovingAverage"
        best_name = min(model_results.keys(), key=lambda k: model_results[k].get("wape", 999.0))
        return best_name


model_evaluator = ModelEvaluator()
