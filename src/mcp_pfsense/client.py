"""pfSense REST API client wrapper."""

from __future__ import annotations

from typing import Any

import httpx

from mcp_pfsense.config import PfSenseConfig


class PfSenseClient:
    """Thin wrapper around the pfSense REST API (pfrest package, API v2).

    Uses Basic Auth and communicates via JSON with the /api/v2 endpoints.

    pfrest v2 exposes two endpoint shapes per resource: a singular endpoint
    (``/firewall/rule``) that operates on one object addressed by ``id`` (plus
    ``parent_id`` for child objects), and a plural endpoint
    (``/firewall/rules``) that lists the collection. Reads go to the plural
    endpoints; creates and deletes go to the singular ones. Write operations
    pass ``apply=true`` so the change takes effect immediately instead of
    staying pending.
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
        return self._get("/interfaces")

    # --- Firewall ---

    def get_firewall_rules(self) -> dict[str, Any]:
        """List all firewall rules."""
        return self._get("/firewall/rules")

    def create_firewall_rule(self, **params: Any) -> dict[str, Any]:
        """Create a firewall rule and apply the filter reload."""
        return self._post("/firewall/rule", apply=True, **params)

    def delete_firewall_rule(self, rule_id: int) -> dict[str, Any]:
        """Delete a firewall rule by ID and apply the filter reload."""
        return self._delete("/firewall/rule", id=rule_id, apply=True)

    # --- DHCP ---

    def get_dhcp_leases(self) -> dict[str, Any]:
        """List active DHCP leases."""
        return self._get("/status/dhcp_server/leases")

    def get_dhcp_static_mappings(self, interface: str | None = None) -> dict[str, Any]:
        """List DHCP static mappings, optionally for one DHCP server (interface).

        Static mappings are child objects of a DHCP server, so the interface is
        the ``parent_id`` in pfrest terms.
        """
        if interface:
            return self._get("/services/dhcp_server/static_mappings", parent_id=interface)
        return self._get("/services/dhcp_server/static_mappings")

    def create_dhcp_static_mapping(self, interface: str, **params: Any) -> dict[str, Any]:
        """Create a DHCP static mapping on the given interface's DHCP server."""
        return self._post(
            "/services/dhcp_server/static_mapping",
            parent_id=interface,
            apply=True,
            **params,
        )

    def delete_dhcp_static_mapping(self, interface: str, mapping_id: int) -> dict[str, Any]:
        """Delete a DHCP static mapping by interface (parent) and ID."""
        return self._delete(
            "/services/dhcp_server/static_mapping",
            parent_id=interface,
            id=mapping_id,
            apply=True,
        )

    # --- DNS ---

    def get_dns_host_overrides(self) -> dict[str, Any]:
        """List DNS Resolver host overrides."""
        return self._get("/services/dns_resolver/host_overrides")

    def create_dns_host_override(self, **params: Any) -> dict[str, Any]:
        """Create a DNS host override and apply the resolver reload."""
        return self._post("/services/dns_resolver/host_override", apply=True, **params)

    def delete_dns_host_override(self, override_id: int) -> dict[str, Any]:
        """Delete a DNS host override by ID and apply the resolver reload."""
        return self._delete("/services/dns_resolver/host_override", id=override_id, apply=True)

    # --- Gateways ---

    def get_gateway_status(self) -> dict[str, Any]:
        """Get gateway status (dual-WAN health)."""
        return self._get("/status/gateways")

    # --- ARP ---

    def get_arp_table(self) -> dict[str, Any]:
        """Get ARP table (connected devices)."""
        return self._get("/diagnostics/arp_table")

    # --- Services ---

    def get_services_status(self) -> dict[str, Any]:
        """List all services and their status."""
        return self._get("/status/services")

    def restart_service(self, name: str) -> dict[str, Any]:
        """Restart a service by name."""
        return self._post("/status/service", name=name, action="restart")

    # --- Firewall Aliases ---

    def get_firewall_aliases(self) -> dict[str, Any]:
        """List firewall aliases."""
        return self._get("/firewall/aliases")
