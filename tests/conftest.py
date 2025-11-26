"""Pytest configuration and fixtures for API tests."""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to a known state before each test."""
    # Store original activities
    original_activities = {
        k: {"description": v["description"],
            "schedule": v["schedule"],
            "max_participants": v["max_participants"],
            "participants": v["participants"].copy()}
        for k, v in activities.items()
    }
    
    yield
    
    # Restore activities after test
    for key in activities:
        activities[key]["participants"] = original_activities[key]["participants"].copy()
