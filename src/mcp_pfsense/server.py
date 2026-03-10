"""MCP server for pfSense firewall management."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from mcp_pfsense.client import PfSenseClient
from mcp_pfsense.config import PfSenseConfig
from mcp_pfsense.tools import dhcp, dns, firewall, monitoring, system

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
) -> dict[str, Any]:
    """Add a firewall rule. Type is 'pass', 'block', or 'reject'."""
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
    )


@mcp.tool()
def delete_firewall_rule(rule_id: int, confirm: bool = False) -> dict[str, Any]:
    """Delete a firewall rule by tracker ID. Requires confirm=true."""
    return firewall.delete_firewall_rule(_get_client(), rule_id=rule_id, confirm=confirm)


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
    """List DHCP static mappings (IP reservations), optionally filtered by interface."""
    return dhcp.list_dhcp_static_mappings(_get_client(), interface=interface)


@mcp.tool()
def add_dhcp_static_mapping(
    interface: str,
    mac: str,
    ipaddr: str,
    hostname: str = "",
    descr: str = "",
) -> dict[str, Any]:
    """Create a DHCP static mapping (IP reservation) for a MAC address."""
    return dhcp.add_dhcp_static_mapping(
        _get_client(),
        interface=interface,
        mac=mac,
        ipaddr=ipaddr,
        hostname=hostname,
        descr=descr,
    )


@mcp.tool()
def delete_dhcp_static_mapping(mapping_id: int, confirm: bool = False) -> dict[str, Any]:
    """Delete a DHCP static mapping by ID. Requires confirm=true."""
    return dhcp.delete_dhcp_static_mapping(_get_client(), mapping_id=mapping_id, confirm=confirm)


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
) -> dict[str, Any]:
    """Create a DNS host override entry in Unbound DNS Resolver."""
    return dns.add_dns_host_override(
        _get_client(),
        host=host,
        domain=domain,
        ip=ip,
        descr=descr,
    )


@mcp.tool()
def delete_dns_host_override(override_id: int, confirm: bool = False) -> dict[str, Any]:
    """Delete a DNS host override by ID. Requires confirm=true."""
    return dns.delete_dns_host_override(_get_client(), override_id=override_id, confirm=confirm)


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
