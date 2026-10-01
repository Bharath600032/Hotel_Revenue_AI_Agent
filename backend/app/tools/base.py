"""
Abstract base class for all Agent Tools.
"""
from typing import Any, Dict, Type
from pydantic import BaseModel
from sqlalchemy.orm import Session


class BaseTool:
    """Base class for AI Agent function-calling tools."""

    name: str
    description: str
    args_schema: Type[BaseModel]

    def execute(self, db: Session, **kwargs) -> Dict[str, Any]:
        """Execute tool logic and return JSON serializable result dictionary."""
        raise NotImplementedError
