"""DHCP management tools."""

from __future__ import annotations

from typing import Any

from mcp_pfsense.client import PfSenseClient


def list_dhcp_leases(client: PfSenseClient) -> list[dict[str, Any]]:
    """List active DHCP leases showing IP, MAC, hostname, and lease times."""
    result = client.get_dhcp_leases()
    data = result.get("data", [])
    if isinstance(data, list):
        return data
    return [data] if data else []


def list_dhcp_static_mappings(
    client: PfSenseClient,
    interface: str | None = None,
) -> list[dict[str, Any]]:
    """List DHCP static mappings (IP reservations), optionally filtered by interface."""
    result = client.get_dhcp_static_mappings(interface=interface)
    data = result.get("data", [])
    if isinstance(data, list):
        return data
    return [data] if data else []


def add_dhcp_static_mapping(
    client: PfSenseClient,
    interface: str,
    mac: str,
    ipaddr: str,
    hostname: str = "",
    descr: str = "",
) -> dict[str, Any]:
    """Create a DHCP static mapping (IP reservation) for a MAC address."""
    params: dict[str, Any] = {
        "interface": interface,
        "mac": mac,
        "ipaddr": ipaddr,
    }
    if hostname:
        params["hostname"] = hostname
    if descr:
        params["descr"] = descr

    result = client.create_dhcp_static_mapping(**params)
    data: dict[str, Any] = result.get("data", result)
    return data


def delete_dhcp_static_mapping(
    client: PfSenseClient,
    mapping_id: int,
    confirm: bool = False,
) -> dict[str, Any]:
    """Delete a DHCP static mapping by ID."""
    if not confirm:
        return {
            "warning": f"This will delete DHCP static mapping with ID {mapping_id}. "
            f"Call again with confirm=true to proceed.",
            "mapping_id": mapping_id,
        }

    result = client.delete_dhcp_static_mapping(mapping_id)
    return {
        "success": True,
        "mapping_id": mapping_id,
        "message": f"DHCP static mapping {mapping_id} deleted.",
        "data": result.get("data", {}),
    }
