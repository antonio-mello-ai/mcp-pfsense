# mcp-pfsense

[![PyPI](https://img.shields.io/pypi/v/mcp-pfsense)](https://pypi.org/project/mcp-pfsense/)
[![Python](https://img.shields.io/pypi/pyversions/mcp-pfsense)](https://pypi.org/project/mcp-pfsense/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

MCP server for managing **pfSense firewalls** through AI assistants like Claude, ChatGPT, and Copilot.

> **Requires**: [pfrest](https://github.com/pfrest/pfSense-pkg-RESTAPI) package installed on your pfSense instance (provides the REST API).

## Features

**17 tools** across 6 categories:

| Category | Tools | Description |
|----------|-------|-------------|
| **System** | `get_system_status`, `get_interfaces` | Version, CPU, memory, uptime, temperature, network interfaces |
| **Firewall** | `list_firewall_rules`, `add_firewall_rule`, `delete_firewall_rule`, `list_firewall_aliases` | Rule management with interface filtering, alias listing |
| **DHCP** | `list_dhcp_leases`, `list_dhcp_static_mappings`, `add_dhcp_static_mapping`, `delete_dhcp_static_mapping` | Active leases, IP reservations |
| **DNS** | `list_dns_host_overrides`, `add_dns_host_override`, `delete_dns_host_override` | Unbound DNS Resolver host overrides |
| **Monitoring** | `get_gateway_status`, `get_arp_table`, `list_services` | Gateway health, connected devices, service status |
| **Services** | `restart_service` | Restart any pfSense service |

### Safety

All destructive operations (delete rules, delete mappings, restart services) require **two-step confirmation** — the tool returns a warning on first call and only executes when called again with `confirm=true`.

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
- *"Create a firewall rule to allow TCP port 8080 on LAN"*
- *"Reserve IP 10.10.10.60 for MAC aa:bb:cc:dd:ee:20"*

## API Compatibility

- **pfSense**: 2.7.x and 2.8.x
- **pfrest**: v2.7.0 or later (REST API v2). Listing DHCP static mappings uses the `/services/dhcp_server/static_mappings` collection endpoint, which pfrest added in v2.7.0; every other tool works with any v2.x release.
- **Python**: 3.11+

The endpoint each tool calls is pinned by `tests/test_client_endpoints.py`, derived from the pfrest v2 endpoint definitions. Versions before 0.1.2 called several endpoints that do not exist in pfrest v2 (see Troubleshooting).

> **Note**: pfrest runs on nginx (port 80 by default), separate from the pfSense WebGUI (lighttpd on port 443). If your pfrest is configured on a non-standard port, set `PFSENSE_PORT` and `PFSENSE_SCHEME` accordingly.

## Troubleshooting

### Only `get_system_status` and `get_arp_table` work; everything else returns 400/404

mcp-pfsense 0.1.1 and earlier called singular endpoints for listing (`/interface`, `/firewall/rule`, `/firewall/alias`) and legacy paths that pfrest v2 does not serve (`/status/dhcp_leases`, `/services/dhcpd/static_mapping`, `/services/unbound/host_override`, `/status/gateway`, `/status/service` for GET). Upgrade to 0.1.2 or later.

### `403` on `list_services` or other reads

pfrest checks the privileges of the API user per endpoint. Grant the user the `api-v2-*` privileges for the endpoints you need (or `page-all` for full access) under **System → User Manager**.

### `ModuleNotFoundError: No module named 'mcp.server.fastmcp'`

The MCP Python SDK 2.0 removed the module that mcp-pfsense 0.1.1 and earlier import, so fresh installs (`uvx mcp-pfsense`, `pip install`) failed on startup. Upgrade to 0.1.2 or later, which pins `mcp<2`. If you must stay on an older mcp-pfsense: `uvx --with "mcp<2" mcp-pfsense`.

### Firewall, DHCP, or DNS changes do not take effect

Write tools send `apply=true`, so pfrest reloads the affected subsystem right away. If a change still shows as pending, check the pfrest **Settings → Apply changes** behaviour and confirm the API user is allowed to apply.

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
