"""System discovery tools."""

from __future__ import annotations

from typing import Any

from mcp_pfsense.client import PfSenseClient


def get_system_status(client: PfSenseClient) -> dict[str, Any]:
    """Get pfSense system status including version, CPU, memory, uptime, and temperature."""
    version = client.get_system_version()
    status = client.get_system_status()
    return {
        "version": version.get("data", {}),
        "system": status.get("data", {}),
    }


def get_interfaces(client: PfSenseClient) -> list[dict[str, Any]]:
    """List all network interfaces with status and configuration."""
    result = client.get_interfaces()
    data = result.get("data", [])
    if isinstance(data, list):
        return data
    return [data] if data else []
