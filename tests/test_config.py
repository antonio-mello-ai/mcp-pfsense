"""Tests for configuration."""

from __future__ import annotations

from mcp_pfsense.config import PfSenseConfig


def test_config_defaults() -> None:
    config = PfSenseConfig(host="10.10.10.1", password="test")

    assert config.host == "10.10.10.1"
    assert config.username == "admin"
    assert config.port == 443
    assert config.verify_ssl is False
    assert config.scheme == "https"


def test_config_base_url() -> None:
    config = PfSenseConfig(host="10.10.10.1", password="test")

    assert config.base_url == "https://10.10.10.1:443/api/v2"


def test_config_custom_values() -> None:
    config = PfSenseConfig(
        host="firewall.local",
        username="apiuser",
        password="secret",
        port=8443,
        scheme="https",
    )

    assert config.base_url == "https://firewall.local:8443/api/v2"
