"""
Tool Registry managing registration, LLM function-calling declarations, and tool execution logging.
"""
import time
import uuid
from typing import Any, Dict, List, Optional, Type
from sqlalchemy.orm import Session

from app.tools.base import BaseTool
from app.tools.revenue_tools import (
    GetHotelProfileTool,
    GetRoomTypesTool,
    GetInventoryTool,
    GetReservationsTool,
    GetBookingPaceTool,
    CalculateOccupancyTool,
    CalculateADRTool,
    CalculateRevPARTool,
    GetHistoricalRatesTool,
    GetHolidayDataTool,
    GetEventDataTool,
    GetCompetitorRatesTool,
    GetWeatherTool,
    RunDemandForecastTool,
    CalculatePricingRecommendationTool,
    ValidatePriceGuardrailsTool,
    GetHotelPoliciesTool,
    SearchKnowledgeBaseTool,
    GenerateRevenueReportTool,
    ExportRecommendationsTool,
    RequestHumanApprovalTool,
    RecordFeedbackTool,
)
from app.models.ai import AgentToolCalls
from app.core.logging import get_logger

logger = get_logger("app.tools.registry")


import json
from datetime import date, datetime
from decimal import Decimal
from enum import Enum


def make_json_serializable(obj: Any) -> Any:
    """Fast JSON-compatible primitive conversion using C-optimized json.dumps fallback."""
    if obj is None or isinstance(obj, (int, float, str, bool)):
        return obj
    try:
        return json.loads(json.dumps(obj, default=str))
    except Exception:
        return str(obj)


class ToolRegistry:
    """Central registry holding all 22 specialized agent tools."""

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._register_default_tools()

    def register(self, tool: BaseTool) -> None:
        self._tools[tool.name] = tool

    def get_tool(self, tool_name: str) -> BaseTool:
        if tool_name not in self._tools:
            raise KeyError(f"Tool '{tool_name}' is not registered.")
        return self._tools[tool_name]

    def list_tools(self) -> List[BaseTool]:
        return list(self._tools.values())

    def get_llm_tool_declarations(self) -> List[Dict[str, Any]]:
        """Export tool declarations in standard LLM function-calling schema."""
        declarations = []
        for name, tool in self._tools.items():
            schema = tool.args_schema.model_json_schema()
            declarations.append(
                {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": {
                        "type": "object",
                        "properties": schema.get("properties", {}),
                        "required": schema.get("required", []),
                    },
                }
            )
        return declarations

    def execute_tool(
        self, db: Session, tool_name: str, arguments: Dict[str, Any], agent_run_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute tool by name, measure latency, log tool call, and catch exceptions cleanly.
        """
        start_time = time.time()
        tool_call_id = f"tc_{uuid.uuid4().hex[:10]}"

        logger.info("tool_execution_started", tool_name=tool_name, tool_call_id=tool_call_id)

        try:
            tool = self.get_tool(tool_name)
            result = tool.execute(db, **arguments)
            status_str = "SUCCESS"
        except Exception as exc:
            logger.error("tool_execution_failed", tool_name=tool_name, error=str(exc))
            result = {"error": f"Tool '{tool_name}' execution error: {str(exc)}"}
            status_str = "FAILED"

        execution_time_ms = round((time.time() - start_time) * 1000.0, 2)

        # Log Tool Call in DB if agent_run_id provided
        if agent_run_id:
            safe_args = make_json_serializable(arguments)
            safe_result = make_json_serializable(result)
            db_call = AgentToolCalls(
                tool_call_id=tool_call_id,
                agent_run_id=agent_run_id,
                tool_name=tool_name,
                arguments=safe_args,
                result=safe_result,
                status=status_str,
                execution_time_ms=execution_time_ms,
            )
            db.add(db_call)
            db.commit()

        return {
            "tool_call_id": tool_call_id,
            "tool_name": tool_name,
            "status": status_str,
            "execution_time_ms": execution_time_ms,
            "result": result,
        }

    def _register_default_tools(self) -> None:
        tools = [
            GetHotelProfileTool(),
            GetRoomTypesTool(),
            GetInventoryTool(),
            GetReservationsTool(),
            GetBookingPaceTool(),
            CalculateOccupancyTool(),
            CalculateADRTool(),
            CalculateRevPARTool(),
            GetHistoricalRatesTool(),
            GetHolidayDataTool(),
            GetEventDataTool(),
            GetCompetitorRatesTool(),
            GetWeatherTool(),
            RunDemandForecastTool(),
            CalculatePricingRecommendationTool(),
            ValidatePriceGuardrailsTool(),
            GetHotelPoliciesTool(),
            SearchKnowledgeBaseTool(),
            GenerateRevenueReportTool(),
            ExportRecommendationsTool(),
            RequestHumanApprovalTool(),
            RecordFeedbackTool(),
        ]
        for t in tools:
            self.register(t)


tool_registry = ToolRegistry()
