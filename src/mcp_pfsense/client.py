"""pfSense REST API client wrapper."""

from __future__ import annotations

from typing import Any

import httpx

from mcp_pfsense.config import PfSenseConfig


class PfSenseClient:
    """Thin wrapper around the pfSense REST API (pfrest package).

    Uses Basic Auth and communicates via JSON with the /api/v2 endpoints.
    """

    def __init__(self, config: PfSenseConfig) -> None:
        self._config = config
        self._client: httpx.Client | None = None

    @property
    def client(self) -> httpx.Client:
        """Lazy-initialize and return the HTTP client."""
        if self._client is None:
            self._client = httpx.Client(
                base_url=self._config.base_url,
                auth=(self._config.username, self._config.password),
                verify=self._config.verify_ssl,
                timeout=30.0,
            )
        return self._client

    def _get(self, path: str, **params: Any) -> dict[str, Any]:
        """Make a GET request and return the response data."""
        resp = self.client.get(path, params=params or None)
        resp.raise_for_status()
        body: dict[str, Any] = resp.json()
        return body

    def _post(self, path: str, **data: Any) -> dict[str, Any]:
        """Make a POST request and return the response data."""
        resp = self.client.post(path, json=data or None)
        resp.raise_for_status()
        body: dict[str, Any] = resp.json()
        return body

    def _patch(self, path: str, **data: Any) -> dict[str, Any]:
        """Make a PATCH request and return the response data."""
        resp = self.client.patch(path, json=data or None)
        resp.raise_for_status()
        body: dict[str, Any] = resp.json()
        return body

    def _delete(self, path: str, **params: Any) -> dict[str, Any]:
        """Make a DELETE request and return the response data."""
        resp = self.client.delete(path, params=params or None)
        resp.raise_for_status()
        body: dict[str, Any] = resp.json()
        return body

    # --- System ---

    def get_system_version(self) -> dict[str, Any]:
        """Get pfSense version info."""
        return self._get("/system/version")

    def get_system_status(self) -> dict[str, Any]:
        """Get system status (CPU, memory, uptime, temperature)."""
        return self._get("/status/system")

    # --- Interfaces ---

    def get_interfaces(self) -> dict[str, Any]:
        """List all network interfaces."""
        return self._get("/interface")

    # --- Firewall ---

    def get_firewall_rules(self) -> dict[str, Any]:
        """List all firewall rules."""
        return self._get("/firewall/rule")

    def create_firewall_rule(self, **params: Any) -> dict[str, Any]:
        """Create a firewall rule."""
        return self._post("/firewall/rule", **params)

    def delete_firewall_rule(self, rule_id: int) -> dict[str, Any]:
        """Delete a firewall rule by tracker ID."""
        return self._delete("/firewall/rule", id=rule_id)

    # --- DHCP ---

    def get_dhcp_leases(self) -> dict[str, Any]:
        """List active DHCP leases."""
        return self._get("/status/dhcp_leases")

    def get_dhcp_static_mappings(self, interface: str | None = None) -> dict[str, Any]:
        """List DHCP static mappings."""
        if interface:
            return self._get("/services/dhcpd/static_mapping", interface=interface)
        return self._get("/services/dhcpd/static_mapping")

    def create_dhcp_static_mapping(self, **params: Any) -> dict[str, Any]:
        """Create a DHCP static mapping."""
        return self._post("/services/dhcpd/static_mapping", **params)

    def delete_dhcp_static_mapping(self, mapping_id: int) -> dict[str, Any]:
        """Delete a DHCP static mapping."""
        return self._delete("/services/dhcpd/static_mapping", id=mapping_id)

    # --- DNS ---

    def get_dns_host_overrides(self) -> dict[str, Any]:
        """List DNS Resolver host overrides."""
        return self._get("/services/unbound/host_override")

    def create_dns_host_override(self, **params: Any) -> dict[str, Any]:
        """Create a DNS host override."""
        return self._post("/services/unbound/host_override", **params)

    def delete_dns_host_override(self, override_id: int) -> dict[str, Any]:
        """Delete a DNS host override."""
        return self._delete("/services/unbound/host_override", id=override_id)

    # --- Gateways ---

    def get_gateway_status(self) -> dict[str, Any]:
        """Get gateway status (dual-WAN health)."""
        return self._get("/status/gateway")

    # --- ARP ---

    def get_arp_table(self) -> dict[str, Any]:
        """Get ARP table (connected devices)."""
        return self._get("/diagnostics/arp_table")

    # --- Services ---

    def get_services_status(self) -> dict[str, Any]:
        """List all services and their status."""
        return self._get("/status/service")

    def restart_service(self, name: str) -> dict[str, Any]:
        """Restart a service by name."""
        return self._post("/status/service", name=name, action="restart")

    # --- Firewall Aliases ---

    def get_firewall_aliases(self) -> dict[str, Any]:
        """List firewall aliases."""
        return self._get("/firewall/alias")
