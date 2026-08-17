"""Tests for the pending-changes tools and the staged-by-default write model."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from mcp_pfsense.client import PfSenseClient
from mcp_pfsense.tools import apply, dns, firewall

from . import sample_data


def _mock(client: PfSenseClient, method: str, payload: dict) -> MagicMock:
    resp = MagicMock()
    resp.json.return_value = payload
    resp.raise_for_status = MagicMock()
    getattr(client._client, method).return_value = resp
    return getattr(client._client, method)  # type: ignore[no-any-return]


def test_get_pending_changes(client: PfSenseClient) -> None:
    get = _mock(
        client,
        "get",
        {"code": 200, "status": "ok", "data": {"applied": False, "pending_subsystems": "filter"}},
    )

    result = apply.get_pending_changes(client, "firewall")

    assert result == {"subsystem": "firewall", "applied": False, "pending_subsystems": "filter"}
    get.assert_called_once_with("/firewall/apply", params=None)


def test_apply_changes_requires_confirm(client: PfSenseClient) -> None:
    result = apply.apply_changes(client, "dns", confirm=False)

    assert "warning" in result
    assert result["subsystem"] == "dns"
    client._client.post.assert_not_called()  # type: ignore[union-attr]


def test_apply_changes_confirmed(client: PfSenseClient) -> None:
    post = _mock(client, "post", {"code": 200, "status": "ok", "data": {"applied": True}})

    result = apply.apply_changes(client, "dhcp", confirm=True)

    assert result["success"] is True
    post.assert_called_once_with("/services/dhcp_server/apply", json=None)


@pytest.mark.parametrize("func", [apply.get_pending_changes, apply.apply_changes])
def test_unknown_subsystem_is_rejected(client: PfSenseClient, func) -> None:  # type: ignore[no-untyped-def]
    with pytest.raises(ValueError, match="Unknown subsystem"):
        func(client, "wireguard")


def test_write_is_staged_by_default_and_says_so(client: PfSenseClient) -> None:
    _mock(client, "post", sample_data.DNS_OVERRIDE_CREATED)

    result = dns.add_dns_host_override(client, host="proxmox", domain="home.lan", ip="10.10.10.100")

    assert result["applied"] is False
    assert "apply_changes(subsystem='dns'" in result["pending"]


def test_write_with_apply_reports_applied(client: PfSenseClient) -> None:
    post = _mock(client, "post", sample_data.FIREWALL_RULE_CREATED)

    result = firewall.add_firewall_rule(client, interface="lan", type_="pass", apply=True)

    assert result["applied"] is True
    assert "pending" not in result
    assert post.call_args.kwargs["json"]["apply"] is True
