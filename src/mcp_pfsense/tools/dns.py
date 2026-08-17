"""DNS management tools."""

from __future__ import annotations

from typing import Any

from mcp_pfsense.client import PfSenseClient
from mcp_pfsense.tools.apply import with_apply_state


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
    apply: bool = False,
) -> dict[str, Any]:
    """Create a DNS host override entry in Unbound DNS Resolver.

    Staged unless `apply` is true (applying reloads unbound). pfrest v2 models
    `ip` as a list of addresses, so the single IP given here is wrapped before
    it is sent.
    """
    params: dict[str, Any] = {
        "host": host,
        "domain": domain,
        "ip": [ip],
    }
    if descr:
        params["descr"] = descr

    result = client.create_dns_host_override(apply=apply, **params)
    data: dict[str, Any] = result.get("data", result)
    return with_apply_state(data, "dns", apply)


def delete_dns_host_override(
    client: PfSenseClient,
    override_id: int,
    confirm: bool = False,
    apply: bool = False,
) -> dict[str, Any]:
    """Delete a DNS host override by ID. Staged unless `apply` is true."""
    if not confirm:
        return {
            "warning": f"This will delete DNS host override with ID {override_id}. "
            f"Call again with confirm=true to proceed.",
            "override_id": override_id,
        }

    result = client.delete_dns_host_override(override_id, apply=apply)
    return with_apply_state(
        {
            "success": True,
            "override_id": override_id,
            "message": f"DNS host override {override_id} deleted.",
            "data": result.get("data", {}),
        },
        "dns",
        apply,
    )
