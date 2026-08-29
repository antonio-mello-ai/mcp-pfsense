# Changelog

All notable changes to mcp-pfsense are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow SemVer.

## [Unreleased]

### Added
- `get_firewall_logs(limit, action)` — a strictly read-only monitoring tool that returns recent firewall log entries (time, action, interface, source, destination, port, protocol) from `GET /status/log/firewall`. Supports a `limit` (default 50) and an optional `action` filter (`pass`/`block`) to answer "why was traffic to X blocked?" without dropping into the WebGUI (#5).

## [0.2.0] — 2026-08-17

### Fixed
- Every tool except `get_system_status` and `get_arp_table` failed with 400/404 against a real firewall (#8). The client called singular endpoints where pfrest v2 lists through the plural collection (`/interfaces`, `/firewall/rules`, `/firewall/aliases`) and legacy paths pfrest v2 does not serve (`/status/dhcp_server/leases`, `/services/dhcp_server/static_mapping(s)`, `/services/dns_resolver/host_override(s)`, `/status/gateways`, `/status/services`). Paths are now derived from the pfrest v2 endpoint definitions and pinned by tests.
- `add_firewall_rule` sent `interface` as a string and `add_dns_host_override` sent `ip` as a string; both fields are lists in pfrest v2.
- Startup crash with `mcp` 2.0.0 (`ModuleNotFoundError: No module named 'mcp.server.fastmcp'`): the SDK is now pinned to `>=1.3.0,<2`.

### Changed
- **Writes are staged by default**, mirroring the pfSense WebGUI. `add_*` and `delete_*` accept `apply` (default `false`) and report `applied` / `pending` in their result. Before, writes were staged too, but by accident: the endpoints did not exist, so nothing was ever written.
- **`delete_dhcp_static_mapping` now requires `interface`** (the mapping's `parent_id`) in addition to `mapping_id` — a static mapping belongs to one DHCP server and cannot be addressed by ID alone.

### Added
- `get_pending_changes(subsystem)` and `apply_changes(subsystem, confirm)` for `firewall`, `dhcp` and `dns` (`/firewall/apply`, `/services/dhcp_server/apply`, `/services/dns_resolver/apply`).
- Endpoint contract tests, wire-format tests (real `httpx` request bytes) and a server import/schema smoke test.
- Release-triggered PyPI publish workflow (tests gate the publish; trusted publishing, no stored token).

## [0.1.1] — 2026-03-10

- MCP Registry metadata fix (`server.json`).

## [0.1.0] — 2026-03-10

- Initial release.
