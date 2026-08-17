"""DHCP management tools."""

from __future__ import annotations

from typing import Any

from mcp_pfsense.client import PfSenseClient
from mcp_pfsense.tools.apply import with_apply_state


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
    """List DHCP static mappings (IP reservations), optionally filtered by interface.

    The interface filter is applied server-side (`parent_id` query): mappings are
    children of one DHCP server, so the match is exact and pfrest handles it.
    Each returned mapping carries `parent_id` — that is the value to pass as
    `interface` when deleting it.
    """
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
    apply: bool = False,
) -> dict[str, Any]:
    """Create a DHCP static mapping (IP reservation) for a MAC address.

    Staged unless `apply` is true (applying restarts dhcpd).
    """
    params: dict[str, Any] = {
        "mac": mac,
        "ipaddr": ipaddr,
    }
    if hostname:
        params["hostname"] = hostname
    if descr:
        params["descr"] = descr

    result = client.create_dhcp_static_mapping(interface, apply=apply, **params)
    data: dict[str, Any] = result.get("data", result)
    return with_apply_state(data, "dhcp", apply)


def delete_dhcp_static_mapping(
    client: PfSenseClient,
    interface: str,
    mapping_id: int,
    confirm: bool = False,
    apply: bool = False,
) -> dict[str, Any]:
    """Delete a DHCP static mapping by interface and ID.

    Static mappings belong to a DHCP server (one per interface), so both the
    interface (the mapping's `parent_id`) and the mapping ID are needed to
    address one. Staged unless `apply` is true.
    """
    if not confirm:
        return {
            "warning": f"This will delete DHCP static mapping {mapping_id} on interface "
            f"'{interface}'. Call again with confirm=true to proceed.",
            "interface": interface,
            "mapping_id": mapping_id,
        }

    result = client.delete_dhcp_static_mapping(interface, mapping_id, apply=apply)
    return with_apply_state(
        {
            "success": True,
            "interface": interface,
            "mapping_id": mapping_id,
            "message": f"DHCP static mapping {mapping_id} deleted.",
            "data": result.get("data", {}),
        },
        "dhcp",
        apply,
    )
