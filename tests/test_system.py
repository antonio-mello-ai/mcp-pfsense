"""Tests for system tools."""

from __future__ import annotations

from unittest.mock import MagicMock

from mcp_pfsense.client import PfSenseClient
from mcp_pfsense.tools import system

from . import sample_data


def test_get_system_status(client: PfSenseClient) -> None:
    mock_resp = MagicMock()
    mock_resp.json.side_effect = [sample_data.SYSTEM_VERSION, sample_data.SYSTEM_STATUS]
    mock_resp.raise_for_status = MagicMock()
    client._client.get.return_value = mock_resp  # type: ignore[union-attr]

    result = system.get_system_status(client)

    assert "version" in result
    assert "system" in result
    assert result["version"]["version"] == "2.7.2-RELEASE"


def test_get_interfaces(client: PfSenseClient) -> None:
    mock_resp = MagicMock()
    mock_resp.json.return_value = sample_data.INTERFACES
    mock_resp.raise_for_status = MagicMock()
    client._client.get.return_value = mock_resp  # type: ignore[union-attr]

    result = system.get_interfaces(client)

    assert len(result) == 2
    assert result[0]["name"] == "WAN"
    assert result[1]["name"] == "LAN"


def test_get_interfaces_single_dict(client: PfSenseClient) -> None:
    single = {"code": 200, "data": {"name": "WAN", "if": "igb0"}}
    mock_resp = MagicMock()
    mock_resp.json.return_value = single
    mock_resp.raise_for_status = MagicMock()
    client._client.get.return_value = mock_resp  # type: ignore[union-attr]

    result = system.get_interfaces(client)

    assert len(result) == 1
    assert result[0]["name"] == "WAN"


def test_get_interfaces_empty(client: PfSenseClient) -> None:
    empty = {"code": 200, "data": []}
    mock_resp = MagicMock()
    mock_resp.json.return_value = empty
    mock_resp.raise_for_status = MagicMock()
    client._client.get.return_value = mock_resp  # type: ignore[union-attr]

    result = system.get_interfaces(client)

    assert result == []
