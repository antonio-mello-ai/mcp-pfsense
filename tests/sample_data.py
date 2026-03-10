"""Sample API response data for tests."""

SYSTEM_VERSION = {
    "code": 200,
    "status": "ok",
    "data": {
        "version": "2.7.2-RELEASE",
        "base": "FreeBSD 14.0-CURRENT",
    },
}

SYSTEM_STATUS = {
    "code": 200,
    "status": "ok",
    "data": {
        "cpu_usage": "12%",
        "memory_usage": "45%",
        "uptime": "15 days 3:42:10",
        "temperature": "48C",
    },
}

INTERFACES = {
    "code": 200,
    "status": "ok",
    "data": [
        {
            "name": "WAN",
            "if": "igb0",
            "status": "up",
            "ipaddr": "203.0.113.10",
            "subnet": "24",
        },
        {
            "name": "LAN",
            "if": "igb1",
            "status": "up",
            "ipaddr": "10.10.10.1",
            "subnet": "24",
        },
    ],
}

FIREWALL_RULES = {
    "code": 200,
    "status": "ok",
    "data": [
        {
            "id": 1,
            "interface": "lan",
            "type": "pass",
            "protocol": "tcp",
            "source": "any",
            "destination": "any",
            "destination_port": "443",
            "descr": "Allow HTTPS",
        },
        {
            "id": 2,
            "interface": "wan",
            "type": "block",
            "protocol": "any",
            "source": "any",
            "destination": "any",
            "descr": "Block all inbound",
        },
    ],
}

FIREWALL_RULE_CREATED = {
    "code": 200,
    "status": "ok",
    "data": {
        "id": 3,
        "interface": "lan",
        "type": "pass",
        "protocol": "tcp",
        "destination_port": "80",
        "descr": "Allow HTTP",
    },
}

FIREWALL_RULE_DELETED = {
    "code": 200,
    "status": "ok",
    "data": {},
}

FIREWALL_ALIASES = {
    "code": 200,
    "status": "ok",
    "data": [
        {
            "name": "trusted_hosts",
            "type": "host",
            "address": "10.10.10.50 10.10.10.51",
            "descr": "Trusted hosts",
        },
    ],
}

DHCP_LEASES = {
    "code": 200,
    "status": "ok",
    "data": [
        {
            "ip": "10.10.30.100",
            "mac": "aa:bb:cc:dd:ee:01",
            "hostname": "laptop-home",
            "start": "2026-03-10 08:00:00",
            "end": "2026-03-10 20:00:00",
            "status": "active",
        },
        {
            "ip": "10.10.30.101",
            "mac": "aa:bb:cc:dd:ee:02",
            "hostname": "phone-home",
            "start": "2026-03-10 09:00:00",
            "end": "2026-03-10 21:00:00",
            "status": "active",
        },
    ],
}

DHCP_STATIC_MAPPINGS = {
    "code": 200,
    "status": "ok",
    "data": [
        {
            "id": 1,
            "interface": "lan",
            "mac": "aa:bb:cc:dd:ee:10",
            "ipaddr": "10.10.10.50",
            "hostname": "nas",
            "descr": "NAS Server",
        },
    ],
}

DHCP_MAPPING_CREATED = {
    "code": 200,
    "status": "ok",
    "data": {
        "id": 2,
        "interface": "lan",
        "mac": "aa:bb:cc:dd:ee:20",
        "ipaddr": "10.10.10.60",
        "hostname": "printer",
    },
}

DHCP_MAPPING_DELETED = {
    "code": 200,
    "status": "ok",
    "data": {},
}

DNS_HOST_OVERRIDES = {
    "code": 200,
    "status": "ok",
    "data": [
        {
            "id": 1,
            "host": "nas",
            "domain": "home.lan",
            "ip": "10.10.10.50",
            "descr": "NAS local DNS",
        },
        {
            "id": 2,
            "host": "grafana",
            "domain": "home.lan",
            "ip": "10.10.10.110",
            "descr": "Grafana",
        },
    ],
}

DNS_OVERRIDE_CREATED = {
    "code": 200,
    "status": "ok",
    "data": {
        "id": 3,
        "host": "proxmox",
        "domain": "home.lan",
        "ip": "10.10.10.100",
    },
}

DNS_OVERRIDE_DELETED = {
    "code": 200,
    "status": "ok",
    "data": {},
}

GATEWAY_STATUS = {
    "code": 200,
    "status": "ok",
    "data": [
        {
            "name": "WAN_DHCP",
            "gateway": "203.0.113.1",
            "monitor": "8.8.8.8",
            "delay": "5.2ms",
            "loss": "0.0%",
            "status": "online",
        },
    ],
}

ARP_TABLE = {
    "code": 200,
    "status": "ok",
    "data": [
        {
            "ip": "10.10.10.50",
            "mac": "aa:bb:cc:dd:ee:10",
            "interface": "igb1",
            "hostname": "nas",
        },
        {
            "ip": "10.10.10.100",
            "mac": "aa:bb:cc:dd:ee:30",
            "interface": "igb1",
            "hostname": "proxmox",
        },
    ],
}

SERVICES = {
    "code": 200,
    "status": "ok",
    "data": [
        {"name": "unbound", "description": "DNS Resolver", "status": "running"},
        {"name": "dhcpd", "description": "DHCP Server", "status": "running"},
        {"name": "nginx", "description": "REST API", "status": "running"},
    ],
}

SERVICE_RESTARTED = {
    "code": 200,
    "status": "ok",
    "data": {"name": "unbound", "action": "restart"},
}
