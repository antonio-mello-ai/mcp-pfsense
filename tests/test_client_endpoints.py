"""Endpoint contract for the pfrest v2 REST API.

These tests pin every client method to the exact pfrest v2 URL and parameters.
pfrest v2 uses singular endpoints for single-object operations (addressed by
``id`` and, for child objects, ``parent_id``) and plural endpoints for listing.
Getting these wrong is invisible to the tool-level tests (they mock the HTTP
layer) but breaks every call against a real firewall — see issue #8.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock

import pytest

from mcp_pfsense.client import PfSenseClient


def _ok(client: PfSenseClient, method: str) -> MagicMock:
    resp = MagicMock()
    resp.json.return_value = {"code": 200, "status": "ok", "data": []}
    resp.raise_for_status = MagicMock()
    getattr(client._client, method).return_value = resp
    return getattr(client._client, method)  # type: ignore[no-any-return]


@pytest.mark.parametrize(
    ("call", "path", "params"),
    [
        (lambda c: c.get_system_version(), "/system/version", None),
        (lambda c: c.get_system_status(), "/status/system", None),
        (lambda c: c.get_interfaces(), "/interfaces", None),
        (lambda c: c.get_firewall_rules(), "/firewall/rules", None),
        (lambda c: c.get_firewall_aliases(), "/firewall/aliases", None),
        (lambda c: c.get_dhcp_leases(), "/status/dhcp_server/leases", None),
        (lambda c: c.get_dhcp_static_mappings(), "/services/dhcp_server/static_mappings", None),
        (
            lambda c: c.get_dhcp_static_mappings(interface="lan"),
            "/services/dhcp_server/static_mappings",
            {"parent_id": "lan"},
        ),
        (lambda c: c.get_dns_host_overrides(), "/services/dns_resolver/host_overrides", None),
        (lambda c: c.get_gateway_status(), "/status/gateways", None),
        (lambda c: c.get_arp_table(), "/diagnostics/arp_table", None),
        (lambda c: c.get_services_status(), "/status/services", None),
        (lambda c: c.get_apply_status("firewall"), "/firewall/apply", None),
        (lambda c: c.get_apply_status("dhcp"), "/services/dhcp_server/apply", None),
        (lambda c: c.get_apply_status("dns"), "/services/dns_resolver/apply", None),
    ],
)
def test_get_endpoints(
    client: PfSenseClient,
    call: Callable[[PfSenseClient], Any],
    path: str,
    params: dict[str, Any] | None,
) -> None:
    get = _ok(client, "get")
    call(client)
    get.assert_called_once_with(path, params=params)


@pytest.mark.parametrize(
    ("call", "path", "json"),
    [
        # writes are staged by default (apply=false) ...
        (
            lambda c: c.create_firewall_rule(type="pass", interface=["lan"]),
            "/firewall/rule",
            {"apply": False, "type": "pass", "interface": ["lan"]},
        ),
        # ... and applied only when asked
        (
            lambda c: c.create_firewall_rule(apply=True, type="pass", interface=["lan"]),
            "/firewall/rule",
            {"apply": True, "type": "pass", "interface": ["lan"]},
        ),
        (
            lambda c: c.create_dhcp_static_mapping(
                "lan", mac="aa:bb:cc:dd:ee:ff", ipaddr="10.0.0.5"
            ),
            "/services/dhcp_server/static_mapping",
            {"parent_id": "lan", "apply": False, "mac": "aa:bb:cc:dd:ee:ff", "ipaddr": "10.0.0.5"},
        ),
        (
            lambda c: c.create_dns_host_override(host="nas", domain="home.lan", ip=["10.0.0.5"]),
            "/services/dns_resolver/host_override",
            {"apply": False, "host": "nas", "domain": "home.lan", "ip": ["10.0.0.5"]},
        ),
        (
            lambda c: c.restart_service("unbound"),
            "/status/service",
            {"name": "unbound", "action": "restart"},
        ),
        (lambda c: c.apply_changes("firewall"), "/firewall/apply", None),
        (lambda c: c.apply_changes("dhcp"), "/services/dhcp_server/apply", None),
        (lambda c: c.apply_changes("dns"), "/services/dns_resolver/apply", None),
    ],
)
def test_post_endpoints(
    client: PfSenseClient,
    call: Callable[[PfSenseClient], Any],
    path: str,
    json: dict[str, Any] | None,
) -> None:
    post = _ok(client, "post")
    call(client)
    post.assert_called_once_with(path, json=json)


@pytest.mark.parametrize(
    ("call", "path", "params"),
    [
        (lambda c: c.delete_firewall_rule(7), "/firewall/rule", {"id": 7, "apply": False}),
        (
            lambda c: c.delete_firewall_rule(7, apply=True),
            "/firewall/rule",
            {"id": 7, "apply": True},
        ),
        (
            lambda c: c.delete_dhcp_static_mapping("lan", 2),
            "/services/dhcp_server/static_mapping",
            {"parent_id": "lan", "id": 2, "apply": False},
        ),
        (
            lambda c: c.delete_dns_host_override(4),
            "/services/dns_resolver/host_override",
            {"id": 4, "apply": False},
        ),
    ],
)
def test_delete_endpoints(
    client: PfSenseClient,
    call: Callable[[PfSenseClient], Any],
    path: str,
    params: dict[str, Any],
) -> None:
    delete = _ok(client, "delete")
    call(client)
    delete.assert_called_once_with(path, params=params)
