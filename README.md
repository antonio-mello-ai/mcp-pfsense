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

- **pfSense**: 2.7.x (tested on 2.7.2)
- **pfrest**: v2.x (REST API v2)
- **Python**: 3.11+

> **Note**: pfrest runs on nginx (port 80 by default), separate from the pfSense WebGUI (lighttpd on port 443). If your pfrest is configured on a non-standard port, set `PFSENSE_PORT` and `PFSENSE_SCHEME` accordingly.

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

<!-- mcp-name: mcp-pfsense -->
