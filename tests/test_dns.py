"""Tests for DNS tools."""

from __future__ import annotations

from unittest.mock import MagicMock

from mcp_pfsense.client import PfSenseClient
from mcp_pfsense.tools import dns

from . import sample_data


def test_list_dns_host_overrides(client: PfSenseClient) -> None:
    mock_resp = MagicMock()
    mock_resp.json.return_value = sample_data.DNS_HOST_OVERRIDES
    mock_resp.raise_for_status = MagicMock()
    client._client.get.return_value = mock_resp  # type: ignore[union-attr]

    result = dns.list_dns_host_overrides(client)

    assert len(result) == 2
    assert result[0]["host"] == "nas"
    assert result[1]["host"] == "grafana"


def test_add_dns_host_override(client: PfSenseClient) -> None:
    mock_resp = MagicMock()
    mock_resp.json.return_value = sample_data.DNS_OVERRIDE_CREATED
    mock_resp.raise_for_status = MagicMock()
    client._client.post.return_value = mock_resp  # type: ignore[union-attr]

    result = dns.add_dns_host_override(
        client,
        host="proxmox",
        domain="home.lan",
        ip="10.10.10.100",
    )

    assert result["id"] == 3
    assert result["host"] == "proxmox"


def test_delete_dns_host_override_no_confirm(client: PfSenseClient) -> None:
    result = dns.delete_dns_host_override(client, override_id=1, confirm=False)

    assert "warning" in result
    assert result["override_id"] == 1


def test_delete_dns_host_override_confirmed(client: PfSenseClient) -> None:
    mock_resp = MagicMock()
    mock_resp.json.return_value = sample_data.DNS_OVERRIDE_DELETED
    mock_resp.raise_for_status = MagicMock()
    client._client.delete.return_value = mock_resp  # type: ignore[union-attr]

    result = dns.delete_dns_host_override(client, override_id=1, confirm=True)

    assert result["success"] is True
    assert result["override_id"] == 1
