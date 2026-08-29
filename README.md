# mcp-pfsense

[![PyPI](https://img.shields.io/pypi/v/mcp-pfsense)](https://pypi.org/project/mcp-pfsense/)
[![Python](https://img.shields.io/pypi/pyversions/mcp-pfsense)](https://pypi.org/project/mcp-pfsense/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

MCP server for managing **pfSense firewalls** through AI assistants like Claude, ChatGPT, and Copilot.

> **Requires**: [pfrest](https://github.com/pfrest/pfSense-pkg-RESTAPI) package installed on your pfSense instance (provides the REST API).

## Features

**20 tools** across 7 categories:

| Category | Tools | Description |
|----------|-------|-------------|
| **System** | `get_system_status`, `get_interfaces` | Version, CPU, memory, uptime, temperature, network interfaces |
| **Firewall** | `list_firewall_rules`, `add_firewall_rule`, `delete_firewall_rule`, `list_firewall_aliases` | Rule management with interface filtering, alias listing |
| **DHCP** | `list_dhcp_leases`, `list_dhcp_static_mappings`, `add_dhcp_static_mapping`, `delete_dhcp_static_mapping` | Active leases, IP reservations |
| **DNS** | `list_dns_host_overrides`, `add_dns_host_override`, `delete_dns_host_override` | Unbound DNS Resolver host overrides |
| **Pending changes** | `get_pending_changes`, `apply_changes` | See what is staged per subsystem (firewall, dhcp, dns) and apply it |
| **Monitoring** | `get_gateway_status`, `get_arp_table`, `list_services`, `get_firewall_logs` | Gateway health, connected devices, service status, recent firewall log entries |
| **Services** | `restart_service` | Restart any pfSense service |

### Safety

- **Two-step confirmation** for destructive operations (delete rules, delete mappings, restart services, apply changes): the tool returns a warning on first call and only executes when called again with `confirm=true`.
- **Writes are staged, not live.** Like the pfSense WebGUI, `add_*` and `delete_*` store the change in the config but do not activate it. The tool response says so (`applied: false`, plus a `pending` note). Activate with `apply_changes(subsystem, confirm=true)` — which reloads that subsystem, including anything a human left staged in the WebGUI — or pass `apply=true` on the write itself when you explicitly want a one-shot change. Nothing the assistant does reaches the packet filter without one of those two explicit steps.
- `delete_dhcp_static_mapping` takes the mapping's `interface` (its `parent_id` in `list_dhcp_static_mappings`) and `mapping_id`; a mapping is addressed by both.

## Installation

```bash
# Using uvx (recommended)
uvx mcp-pfsense

# Using pip
pip install mcp-pfsense
```

### Prerequisites

1. **pfSense** with [pfrest](https://github.com/pfrest/pfSense-pkg-RESTAPI) package installed
2. A user account with API access (typically `admin`)

## Configuration

Set environment variables:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PFSENSE_HOST` | Yes | — | pfSense hostname or IP |
| `PFSENSE_PASSWORD` | Yes | — | API user password |
| `PFSENSE_USERNAME` | No | `admin` | API username |
| `PFSENSE_PORT` | No | `443` | API port |
| `PFSENSE_SCHEME` | No | `https` | `http` or `https` |
| `PFSENSE_VERIFY_SSL` | No | `false` | Verify SSL certificate |

### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "pfsense": {
      "command": "uvx",
      "args": ["mcp-pfsense"],
      "env": {
        "PFSENSE_HOST": "10.10.10.1",
        "PFSENSE_PASSWORD": "your-password"
      }
    }
  }
}
```

### Claude Code

```bash
claude mcp add pfsense -- uvx mcp-pfsense
```

Then set environment variables in your shell or `.env` file.

## Usage Examples

Once connected, ask your AI assistant:

- *"What's the pfSense system status?"*
- *"Show me all firewall rules on the LAN interface"*
- *"List active DHCP leases"*
- *"Add a DNS entry for nas.home.lan pointing to 10.10.10.50"*
- *"What devices are connected to the network?"* (ARP table)
- *"Show gateway health and latency"*
- *"Why was traffic to 10.0.0.5:443 blocked?"* (read-only `get_firewall_logs`, optionally `action="block"`)
- *"Create a firewall rule to allow TCP port 8080 on LAN"*
- *"Reserve IP 10.10.10.60 for MAC aa:bb:cc:dd:ee:20"*

## API Compatibility

- **pfSense**: 2.7.x and 2.8.x
- **pfrest**: REST API v2 — any v2.x release, except `list_dhcp_static_mappings`, which needs **v2.7.0 or later** (it uses the `/services/dhcp_server/static_mappings` collection endpoint added in that release).
- **Python**: 3.11+

The endpoint, parameters and encoding each tool uses are pinned by `tests/test_client_endpoints.py` and `tests/test_wire_format.py`, derived from the pfrest v2 endpoint definitions. Versions before 0.2.0 called several endpoints that do not exist in pfrest v2 (see Troubleshooting).

> **Note**: pfrest runs on nginx (port 80 by default), separate from the pfSense WebGUI (lighttpd on port 443). If your pfrest is configured on a non-standard port, set `PFSENSE_PORT` and `PFSENSE_SCHEME` accordingly.

## Troubleshooting

### Only `get_system_status` and `get_arp_table` work; everything else returns 400/404

mcp-pfsense 0.1.1 and earlier called singular endpoints for listing (`/interface`, `/firewall/rule`, `/firewall/alias`) and legacy paths that pfrest v2 does not serve (`/status/dhcp_leases`, `/services/dhcpd/static_mapping`, `/services/unbound/host_override`, `/status/gateway`, `/status/service` for GET). Upgrade to 0.2.0 or later.

### `403` on `list_services` or other reads

pfrest checks the privileges of the API user per endpoint. Grant the user the `api-v2-*` privileges for the endpoints you need (or `page-all` for full access) under **System → User Manager**.

### `ModuleNotFoundError: No module named 'mcp.server.fastmcp'`

The MCP Python SDK 2.0 removed the module that mcp-pfsense 0.1.1 and earlier import, so fresh installs (`uvx mcp-pfsense`, `pip install`) failed on startup. Upgrade to 0.2.0 or later, which pins `mcp<2`. If you must stay on an older mcp-pfsense: `uvx --with "mcp<2" mcp-pfsense`.

### A rule / mapping / override was created but is not in effect

That is the default: writes are staged (see **Safety**). Check with `get_pending_changes(subsystem)` and activate with `apply_changes(subsystem, confirm=true)`, or in the WebGUI. If a write returns 200 but nothing is stored at all, the pfrest **`read_only`** setting is on (System → REST API → Settings).

## Development

```bash
git clone https://github.com/antonio-mello-ai/mcp-pfsense.git
cd mcp-pfsense
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Run tests
pytest

# Lint and type check
ruff check .
mypy src/
```

## License

MIT

<!-- mcp-name: io.github.antonio-mello-ai/mcp-pfsense -->
