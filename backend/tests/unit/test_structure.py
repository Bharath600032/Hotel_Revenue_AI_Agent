"""
Structure verification unit test for Phase 2.
"""
import pytest
import importlib

REQUIRED_MODULES = [
    "app.main",
    "app.api",
    "app.core",
    "app.db",
    "app.models",
    "app.schemas",
    "app.repositories",
    "app.services",
    "app.agents",
    "app.tools",
    "app.forecasting",
    "app.pricing",
    "app.competitors",
    "app.events",
    "app.holidays",
    "app.rag",
    "app.audit",
    "app.notifications",
    "app.reports",
    "app.imports",
    "app.monitoring",
    "app.utils",
]


@pytest.mark.parametrize("module_name", REQUIRED_MODULES)
def test_module_structure_exists(module_name: str):
    """Test that all required backend architectural packages exist and import cleanly."""
    mod = importlib.import_module(module_name)
    assert mod is not None
