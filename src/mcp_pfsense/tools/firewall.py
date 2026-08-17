"""Firewall rule tools."""

from __future__ import annotations

from typing import Any

from mcp_pfsense.client import PfSenseClient
from mcp_pfsense.tools.apply import with_apply_state


def list_firewall_rules(
    client: PfSenseClient,
    interface: str | None = None,
) -> list[dict[str, Any]]:
    """List firewall rules, optionally filtered by interface."""
    result = client.get_firewall_rules()
    rules: list[dict[str, Any]] = result.get("data", [])
    if interface:
        rules = [r for r in rules if _rule_matches_interface(r, interface)]
    return rules


def _rule_matches_interface(rule: dict[str, Any], interface: str) -> bool:
    """pfrest v2 returns `interface` as a list (the field is many-valued).

    Filtering happens client-side because a rule can be bound to several
    interfaces; a plain `interface=<name>` query would only match rules bound
    to exactly that one. Tolerates a bare string or a missing value.
    """
    value = rule.get("interface") or []
    if isinstance(value, str):
        value = [value]
    return interface in value


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
    apply: bool = False,
) -> dict[str, Any]:
    """Add a firewall rule.

    The rule is staged (like the WebGUI) unless `apply` is true. pfrest v2
    models `interface` as a list, so the single interface given here is wrapped
    before it is sent.
    """
    params: dict[str, Any] = {
        "interface": [interface],
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

    result = client.create_firewall_rule(apply=apply, **params)
    data: dict[str, Any] = result.get("data", result)
    return with_apply_state(data, "firewall", apply)


def delete_firewall_rule(
    client: PfSenseClient,
    rule_id: int,
    confirm: bool = False,
    apply: bool = False,
) -> dict[str, Any]:
    """Delete a firewall rule by its ID (as returned by list_firewall_rules).

    Staged unless `apply` is true.
    """
    if not confirm:
        return {
            "warning": f"This will delete firewall rule with ID {rule_id}. "
            f"Call again with confirm=true to proceed.",
            "rule_id": rule_id,
        }

    result = client.delete_firewall_rule(rule_id, apply=apply)
    return with_apply_state(
        {
            "success": True,
            "rule_id": rule_id,
            "message": f"Firewall rule {rule_id} deleted.",
            "data": result.get("data", {}),
        },
        "firewall",
        apply,
    )


def list_firewall_aliases(client: PfSenseClient) -> list[dict[str, Any]]:
    """List firewall aliases (IP groups, port groups, URL lists)."""
    result = client.get_firewall_aliases()
    data = result.get("data", [])
    if isinstance(data, list):
        return data
    return [data] if data else []
