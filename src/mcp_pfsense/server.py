"""MCP server for pfSense firewall management."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from mcp_pfsense.client import PfSenseClient
from mcp_pfsense.config import PfSenseConfig
from mcp_pfsense.tools import apply, dhcp, dns, firewall, monitoring, system

mcp = FastMCP(
    "mcp-pfsense",
    instructions="Manage pfSense firewalls through AI assistants",
)

_client: PfSenseClient | None = None


def _get_client() -> PfSenseClient:
    """Get or create the pfSense client singleton."""
    global _client  # noqa: PLW0603
    if _client is None:
        config = PfSenseConfig.from_env()
        _client = PfSenseClient(config)
    return _client


# --- System & Interfaces ---


@mcp.tool()
def get_system_status() -> dict[str, Any]:
    """Get pfSense system status including version, CPU, memory, uptime, and temperature."""
    return system.get_system_status(_get_client())


@mcp.tool()
def get_interfaces() -> list[dict[str, Any]]:
    """List all network interfaces with status and configuration."""
    return system.get_interfaces(_get_client())


# --- Firewall ---


@mcp.tool()
def list_firewall_rules(interface: str | None = None) -> list[dict[str, Any]]:
    """List firewall rules, optionally filtered by interface."""
    return firewall.list_firewall_rules(_get_client(), interface=interface)


@mcp.tool()
def add_firewall_rule(
    interface: str,
    type: str,
    ipprotocol: str = "inet",
    protocol: str | None = None,
    source: str = "any",
    destination: str = "any",
    dstport: str | None = None,
    descr: str = "",
    apply: bool = False,
) -> dict[str, Any]:
    """Add a firewall rule. Type is 'pass', 'block', or 'reject'.

    The rule is staged (not active) until apply_changes('firewall') is called
    or apply=true is passed here.
    """
    return firewall.add_firewall_rule(
        _get_client(),
        interface=interface,
        type_=type,
        ipprotocol=ipprotocol,
        protocol=protocol,
        source=source,
        destination=destination,
        dstport=dstport,
        descr=descr,
        apply=apply,
    )


@mcp.tool()
def delete_firewall_rule(
    rule_id: int, confirm: bool = False, apply: bool = False
) -> dict[str, Any]:
    """Delete a firewall rule by its ID (the `id` from list_firewall_rules). Requires confirm=true.

    Staged until apply_changes('firewall') is called or apply=true is passed.
    """
    return firewall.delete_firewall_rule(
        _get_client(), rule_id=rule_id, confirm=confirm, apply=apply
    )


@mcp.tool()
def list_firewall_aliases() -> list[dict[str, Any]]:
    """List firewall aliases (IP groups, port groups, URL lists)."""
    return firewall.list_firewall_aliases(_get_client())


# --- DHCP ---


@mcp.tool()
def list_dhcp_leases() -> list[dict[str, Any]]:
    """List active DHCP leases showing IP, MAC, hostname, and lease times."""
    return dhcp.list_dhcp_leases(_get_client())


@mcp.tool()
def list_dhcp_static_mappings(interface: str | None = None) -> list[dict[str, Any]]:
    """List DHCP static mappings (IP reservations), optionally filtered by interface.

    Each mapping carries `parent_id` (its DHCP server / interface) — pass that as
    `interface` to delete_dhcp_static_mapping.
    """
    return dhcp.list_dhcp_static_mappings(_get_client(), interface=interface)


@mcp.tool()
def add_dhcp_static_mapping(
    interface: str,
    mac: str,
    ipaddr: str,
    hostname: str = "",
    descr: str = "",
    apply: bool = False,
) -> dict[str, Any]:
    """Create a DHCP static mapping (IP reservation) for a MAC address.

    Staged until apply_changes('dhcp') is called or apply=true is passed.
    """
    return dhcp.add_dhcp_static_mapping(
        _get_client(),
        interface=interface,
        mac=mac,
        ipaddr=ipaddr,
        hostname=hostname,
        descr=descr,
        apply=apply,
    )


@mcp.tool()
def delete_dhcp_static_mapping(
    interface: str, mapping_id: int, confirm: bool = False, apply: bool = False
) -> dict[str, Any]:
    """Delete a DHCP static mapping. Requires confirm=true.

    `interface` is the mapping's DHCP server — the `parent_id` value returned by
    list_dhcp_static_mappings; `mapping_id` is its `id` there. Staged until
    apply_changes('dhcp') is called or apply=true is passed.
    """
    return dhcp.delete_dhcp_static_mapping(
        _get_client(), interface=interface, mapping_id=mapping_id, confirm=confirm, apply=apply
    )


# --- DNS ---


@mcp.tool()
def list_dns_host_overrides() -> list[dict[str, Any]]:
    """List DNS Resolver host overrides (local DNS entries)."""
    return dns.list_dns_host_overrides(_get_client())


@mcp.tool()
def add_dns_host_override(
    host: str,
    domain: str,
    ip: str,
    descr: str = "",
    apply: bool = False,
) -> dict[str, Any]:
    """Create a DNS host override entry in Unbound DNS Resolver.

    Staged until apply_changes('dns') is called or apply=true is passed.
    """
    return dns.add_dns_host_override(
        _get_client(),
        host=host,
        domain=domain,
        ip=ip,
        descr=descr,
        apply=apply,
    )


@mcp.tool()
def delete_dns_host_override(
    override_id: int, confirm: bool = False, apply: bool = False
) -> dict[str, Any]:
    """Delete a DNS host override by ID. Requires confirm=true.

    Staged until apply_changes('dns') is called or apply=true is passed.
    """
    return dns.delete_dns_host_override(
        _get_client(), override_id=override_id, confirm=confirm, apply=apply
    )


# --- Pending changes ---


@mcp.tool()
def get_pending_changes(subsystem: str) -> dict[str, Any]:
    """Check whether a subsystem ('firewall', 'dhcp' or 'dns') has staged, unapplied changes."""
    return apply.get_pending_changes(_get_client(), subsystem=subsystem)


@mcp.tool()
def apply_changes(subsystem: str, confirm: bool = False) -> dict[str, Any]:
    """Apply ALL staged changes of a subsystem ('firewall', 'dhcp' or 'dns'). Requires confirm=true.

    This reloads the subsystem, activating every pending change — including any
    a human staged in the pfSense WebGUI and has not reviewed yet.
    """
    return apply.apply_changes(_get_client(), subsystem=subsystem, confirm=confirm)


# --- Monitoring & Diagnostics ---


@mcp.tool()
def get_gateway_status() -> list[dict[str, Any]]:
    """Get gateway status including latency, packet loss, and online state."""
    return monitoring.get_gateway_status(_get_client())


@mcp.tool()
def get_arp_table() -> list[dict[str, Any]]:
    """Get ARP table showing connected devices (IP, MAC, interface)."""
    return monitoring.get_arp_table(_get_client())


@mcp.tool()
def list_services() -> list[dict[str, Any]]:
    """List all services and their running status."""
    return monitoring.list_services(_get_client())


@mcp.tool()
def restart_service(name: str, confirm: bool = False) -> dict[str, Any]:
    """Restart a service by name. Requires confirm=true."""
    return monitoring.restart_service(_get_client(), name=name, confirm=confirm)


def main() -> None:
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
