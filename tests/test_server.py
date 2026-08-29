"""Smoke tests for the MCP server module.

Nothing else imports ``mcp_pfsense.server``, so without this the test suite
cannot notice when the MCP SDK API it depends on changes (``mcp`` 2.0.0
removed ``mcp.server.fastmcp``) — or when a tool's exposed schema drifts.
"""

from __future__ import annotations

import asyncio

from mcp_pfsense import server

EXPECTED_TOOLS = {
    "get_system_status",
    "get_interfaces",
    "list_firewall_rules",
    "add_firewall_rule",
    "delete_firewall_rule",
    "list_firewall_aliases",
    "list_dhcp_leases",
    "list_dhcp_static_mappings",
    "add_dhcp_static_mapping",
    "delete_dhcp_static_mapping",
    "list_dns_host_overrides",
    "add_dns_host_override",
    "delete_dns_host_override",
    "get_pending_changes",
    "apply_changes",
    "get_gateway_status",
    "get_arp_table",
    "list_services",
    "restart_service",
    "get_firewall_logs",
}


def _tools() -> dict[str, dict]:
    return {t.name: t.inputSchema for t in asyncio.run(server.mcp.list_tools())}


def test_server_module_imports() -> None:
    assert server.mcp.name == "mcp-pfsense"


def test_server_registers_exactly_the_expected_tools() -> None:
    assert set(_tools()) == EXPECTED_TOOLS


def test_delete_dhcp_static_mapping_requires_interface() -> None:
    schema = _tools()["delete_dhcp_static_mapping"]
    assert set(schema["required"]) == {"interface", "mapping_id"}


def test_write_tools_expose_apply_flag_defaulting_to_false() -> None:
    tools = _tools()
    for name in (
        "add_firewall_rule",
        "delete_firewall_rule",
        "add_dhcp_static_mapping",
        "delete_dhcp_static_mapping",
        "add_dns_host_override",
        "delete_dns_host_override",
    ):
        prop = tools[name]["properties"]["apply"]
        assert prop["type"] == "boolean" and prop["default"] is False, name


def test_apply_changes_requires_confirm_flag() -> None:
    schema = _tools()["apply_changes"]
    assert schema["properties"]["confirm"]["default"] is False
    assert schema["required"] == ["subsystem"]
