"""Shared test fixtures."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from mcp_pfsense.client import PfSenseClient
from mcp_pfsense.config import PfSenseConfig


@pytest.fixture
def config() -> PfSenseConfig:
    """Create a test config."""
    return PfSenseConfig(
        host="10.10.10.1",
        username="admin",
        password="testpass",
        port=443,
        verify_ssl=False,
    )


@pytest.fixture
def client(config: PfSenseConfig) -> PfSenseClient:
    """Create a PfSenseClient with a mocked HTTP client."""
    c = PfSenseClient(config)
    c._client = MagicMock()
    return c
