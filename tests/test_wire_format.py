"""What actually goes on the wire.

The other tests mock ``httpx.Client`` and assert on Python objects. pfrest is
strict about the encoding: GET/DELETE parameters travel in the query string
and are type-inferred (``apply=true`` — the lowercase literal — becomes boolean
true, anything else stays a string and fails the ``=== true`` check server
side); POST bodies are JSON. These tests drive a real ``httpx.Client`` through
``httpx.MockTransport`` and assert on the bytes.
"""

from __future__ import annotations

import json

import httpx

from mcp_pfsense.client import PfSenseClient
from mcp_pfsense.config import PfSenseConfig


def _client_capturing(requests: list[httpx.Request]) -> PfSenseClient:
    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"code": 200, "status": "ok", "data": {}})

    config = PfSenseConfig(
        host="10.10.10.1", username="admin", password="pw", port=80, scheme="http"
    )
    client = PfSenseClient(config)
    client._client = httpx.Client(base_url=config.base_url, transport=httpx.MockTransport(handler))
    return client


def test_delete_sends_ids_and_apply_flag_in_query_string() -> None:
    seen: list[httpx.Request] = []
    client = _client_capturing(seen)

    client.delete_dhcp_static_mapping("lan", 2, apply=True)

    assert len(seen) == 1
    req = seen[0]
    assert req.method == "DELETE"
    assert req.url.path == "/api/v2/services/dhcp_server/static_mapping"
    assert req.url.query == b"parent_id=lan&id=2&apply=true"
    assert req.content == b""


def test_staged_delete_sends_apply_false() -> None:
    seen: list[httpx.Request] = []
    client = _client_capturing(seen)

    client.delete_firewall_rule(7)

    assert seen[0].url.query == b"id=7&apply=false"


def test_get_with_parent_id_filter() -> None:
    seen: list[httpx.Request] = []
    client = _client_capturing(seen)

    client.get_dhcp_static_mappings(interface="lan")

    assert seen[0].method == "GET"
    assert seen[0].url.path == "/api/v2/services/dhcp_server/static_mappings"
    assert seen[0].url.query == b"parent_id=lan"


def test_post_sends_json_body_with_lists_and_apply() -> None:
    seen: list[httpx.Request] = []
    client = _client_capturing(seen)

    client.create_dns_host_override(host="nas", domain="home.lan", ip=["10.0.0.5"], apply=True)

    req = seen[0]
    assert req.method == "POST"
    assert req.url.path == "/api/v2/services/dns_resolver/host_override"
    assert req.headers["content-type"] == "application/json"
    assert json.loads(req.content) == {
        "apply": True,
        "host": "nas",
        "domain": "home.lan",
        "ip": ["10.0.0.5"],
    }


def test_apply_endpoint_post_has_no_body() -> None:
    seen: list[httpx.Request] = []
    client = _client_capturing(seen)

    client.apply_changes("firewall")

    assert seen[0].method == "POST"
    assert seen[0].url.path == "/api/v2/firewall/apply"
    assert seen[0].content == b""
