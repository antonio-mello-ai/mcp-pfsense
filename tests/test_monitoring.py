"""Tests for monitoring tools."""

from __future__ import annotations

from unittest.mock import MagicMock

from mcp_pfsense.client import PfSenseClient
from mcp_pfsense.tools import monitoring

from . import sample_data


def test_get_gateway_status(client: PfSenseClient) -> None:
    mock_resp = MagicMock()
    mock_resp.json.return_value = sample_data.GATEWAY_STATUS
    mock_resp.raise_for_status = MagicMock()
    client._client.get.return_value = mock_resp  # type: ignore[union-attr]

    result = monitoring.get_gateway_status(client)

    assert len(result) == 1
    assert result[0]["status"] == "online"


def test_get_arp_table(client: PfSenseClient) -> None:
    mock_resp = MagicMock()
    mock_resp.json.return_value = sample_data.ARP_TABLE
    mock_resp.raise_for_status = MagicMock()
    client._client.get.return_value = mock_resp  # type: ignore[union-attr]

    result = monitoring.get_arp_table(client)

    assert len(result) == 2
    assert result[0]["hostname"] == "nas"
    assert result[1]["hostname"] == "proxmox"


def test_list_services(client: PfSenseClient) -> None:
    mock_resp = MagicMock()
    mock_resp.json.return_value = sample_data.SERVICES
    mock_resp.raise_for_status = MagicMock()
    client._client.get.return_value = mock_resp  # type: ignore[union-attr]

    result = monitoring.list_services(client)

    assert len(result) == 3
    assert all(s["status"] == "running" for s in result)


def test_restart_service_no_confirm(client: PfSenseClient) -> None:
    result = monitoring.restart_service(client, name="unbound", confirm=False)

    assert "warning" in result
    assert result["service"] == "unbound"


def test_restart_service_confirmed(client: PfSenseClient) -> None:
    mock_resp = MagicMock()
    mock_resp.json.return_value = sample_data.SERVICE_RESTARTED
    mock_resp.raise_for_status = MagicMock()
    client._client.post.return_value = mock_resp  # type: ignore[union-attr]

    result = monitoring.restart_service(client, name="unbound", confirm=True)

    assert result["success"] is True
    assert result["service"] == "unbound"
