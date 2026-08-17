"""Smoke tests for the MCP server module.

Nothing else imports ``mcp_pfsense.server``, so without this the test suite
cannot notice when the MCP SDK API it depends on changes (``mcp`` 2.0.0
removed ``mcp.server.fastmcp``).
"""

from __future__ import annotations

import asyncio

from mcp_pfsense import server


def test_server_module_imports() -> None:
    assert server.mcp.name == "mcp-pfsense"


def test_server_registers_tools() -> None:
    tools = asyncio.run(server.mcp.list_tools())
    names = {tool.name for tool in tools}

    assert len(names) == 17
    for expected in ("get_system_status", "list_firewall_rules", "delete_dhcp_static_mapping"):
        assert expected in names
