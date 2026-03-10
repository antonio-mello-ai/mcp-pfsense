"""DNS management tools."""

from __future__ import annotations

from typing import Any

from mcp_pfsense.client import PfSenseClient


def list_dns_host_overrides(client: PfSenseClient) -> list[dict[str, Any]]:
    """List DNS Resolver host overrides (local DNS entries)."""
    result = client.get_dns_host_overrides()
    data = result.get("data", [])
    if isinstance(data, list):
        return data
    return [data] if data else []


def add_dns_host_override(
    client: PfSenseClient,
    host: str,
    domain: str,
    ip: str,
    descr: str = "",
) -> dict[str, Any]:
    """Create a DNS host override entry in Unbound DNS Resolver."""
    params: dict[str, Any] = {
        "host": host,
        "domain": domain,
        "ip": ip,
    }
    if descr:
        params["descr"] = descr

    result = client.create_dns_host_override(**params)
    data: dict[str, Any] = result.get("data", result)
    return data


def delete_dns_host_override(
    client: PfSenseClient,
    override_id: int,
    confirm: bool = False,
) -> dict[str, Any]:
    """Delete a DNS host override by ID."""
    if not confirm:
        return {
            "warning": f"This will delete DNS host override with ID {override_id}. "
            f"Call again with confirm=true to proceed.",
            "override_id": override_id,
        }

    result = client.delete_dns_host_override(override_id)
    return {
        "success": True,
        "override_id": override_id,
        "message": f"DNS host override {override_id} deleted.",
        "data": result.get("data", {}),
    }
