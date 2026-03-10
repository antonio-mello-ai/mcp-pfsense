"""Monitoring and diagnostics tools."""

from __future__ import annotations

from typing import Any

from mcp_pfsense.client import PfSenseClient


def get_gateway_status(client: PfSenseClient) -> list[dict[str, Any]]:
    """Get gateway status including latency, packet loss, and online state."""
    result = client.get_gateway_status()
    data = result.get("data", [])
    if isinstance(data, list):
        return data
    return [data] if data else []


def get_arp_table(client: PfSenseClient) -> list[dict[str, Any]]:
    """Get ARP table showing connected devices (IP, MAC, interface)."""
    result = client.get_arp_table()
    data = result.get("data", [])
    if isinstance(data, list):
        return data
    return [data] if data else []


def list_services(client: PfSenseClient) -> list[dict[str, Any]]:
    """List all services and their running status."""
    result = client.get_services_status()
    data = result.get("data", [])
    if isinstance(data, list):
        return data
    return [data] if data else []


def restart_service(
    client: PfSenseClient,
    name: str,
    confirm: bool = False,
) -> dict[str, Any]:
    """Restart a service by name."""
    if not confirm:
        return {
            "warning": f"This will restart service '{name}'. "
            f"Call again with confirm=true to proceed.",
            "service": name,
        }

    result = client.restart_service(name)
    return {
        "success": True,
        "service": name,
        "message": f"Service '{name}' restarted.",
        "data": result.get("data", {}),
    }
