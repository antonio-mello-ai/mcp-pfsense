"""Tests for firewall tools."""

from __future__ import annotations

from unittest.mock import MagicMock

from mcp_pfsense.client import PfSenseClient
from mcp_pfsense.tools import firewall

from . import sample_data


def test_list_firewall_rules(client: PfSenseClient) -> None:
    mock_resp = MagicMock()
    mock_resp.json.return_value = sample_data.FIREWALL_RULES
    mock_resp.raise_for_status = MagicMock()
    client._client.get.return_value = mock_resp  # type: ignore[union-attr]

    result = firewall.list_firewall_rules(client)

    assert len(result) == 2
    assert result[0]["descr"] == "Allow HTTPS"


def test_list_firewall_rules_filter_interface(client: PfSenseClient) -> None:
    mock_resp = MagicMock()
    mock_resp.json.return_value = sample_data.FIREWALL_RULES
    mock_resp.raise_for_status = MagicMock()
    client._client.get.return_value = mock_resp  # type: ignore[union-attr]

    result = firewall.list_firewall_rules(client, interface="lan")

    assert len(result) == 1
    assert result[0]["interface"] == "lan"


def test_add_firewall_rule(client: PfSenseClient) -> None:
    mock_resp = MagicMock()
    mock_resp.json.return_value = sample_data.FIREWALL_RULE_CREATED
    mock_resp.raise_for_status = MagicMock()
    client._client.post.return_value = mock_resp  # type: ignore[union-attr]

    result = firewall.add_firewall_rule(
        client,
        interface="lan",
        type_="pass",
        protocol="tcp",
        dstport="80",
        descr="Allow HTTP",
    )

    assert result["id"] == 3


def test_delete_firewall_rule_no_confirm(client: PfSenseClient) -> None:
    result = firewall.delete_firewall_rule(client, rule_id=1, confirm=False)

    assert "warning" in result
    assert result["rule_id"] == 1


def test_delete_firewall_rule_confirmed(client: PfSenseClient) -> None:
    mock_resp = MagicMock()
    mock_resp.json.return_value = sample_data.FIREWALL_RULE_DELETED
    mock_resp.raise_for_status = MagicMock()
    client._client.delete.return_value = mock_resp  # type: ignore[union-attr]

    result = firewall.delete_firewall_rule(client, rule_id=1, confirm=True)

    assert result["success"] is True
    assert result["rule_id"] == 1


def test_list_firewall_aliases(client: PfSenseClient) -> None:
    mock_resp = MagicMock()
    mock_resp.json.return_value = sample_data.FIREWALL_ALIASES
    mock_resp.raise_for_status = MagicMock()
    client._client.get.return_value = mock_resp  # type: ignore[union-attr]

    result = firewall.list_firewall_aliases(client)

    assert len(result) == 1
    assert result[0]["name"] == "trusted_hosts"
