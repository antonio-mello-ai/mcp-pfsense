"""Firewall rule tools."""

from __future__ import annotations

from typing import Any

from mcp_pfsense.client import PfSenseClient


def list_firewall_rules(
    client: PfSenseClient,
    interface: str | None = None,
) -> list[dict[str, Any]]:
    """List firewall rules, optionally filtered by interface."""
    result = client.get_firewall_rules()
    rules: list[dict[str, Any]] = result.get("data", [])
    if interface:
        rules = [r for r in rules if r.get("interface", "") == interface]
    return rules


def add_firewall_rule(
    client: PfSenseClient,
    interface: str,
    type_: str,
    ipprotocol: str = "inet",
    protocol: str | None = None,
    source: str = "any",
    destination: str = "any",
    dstport: str | None = None,
    descr: str = "",
) -> dict[str, Any]:
    """Add a firewall rule."""
    params: dict[str, Any] = {
        "interface": interface,
        "type": type_,
        "ipprotocol": ipprotocol,
        "source": source,
        "destination": destination,
    }
    if protocol:
        params["protocol"] = protocol
    if dstport:
        params["destination_port"] = dstport
    if descr:
        params["descr"] = descr

    result = client.create_firewall_rule(**params)
    data: dict[str, Any] = result.get("data", result)
    return data


def delete_firewall_rule(
    client: PfSenseClient,
    rule_id: int,
    confirm: bool = False,
) -> dict[str, Any]:
    """Delete a firewall rule by its tracker ID."""
    if not confirm:
        return {
            "warning": f"This will delete firewall rule with ID {rule_id}. "
            f"Call again with confirm=true to proceed.",
            "rule_id": rule_id,
        }

    result = client.delete_firewall_rule(rule_id)
    return {
        "success": True,
        "rule_id": rule_id,
        "message": f"Firewall rule {rule_id} deleted.",
        "data": result.get("data", {}),
    }


def list_firewall_aliases(client: PfSenseClient) -> list[dict[str, Any]]:
    """List firewall aliases (IP groups, port groups, URL lists)."""
    result = client.get_firewall_aliases()
    data = result.get("data", [])
    if isinstance(data, list):
        return data
    return [data] if data else []
