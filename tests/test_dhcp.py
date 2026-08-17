"""Tests for DHCP tools."""

from __future__ import annotations

from unittest.mock import MagicMock

from mcp_pfsense.client import PfSenseClient
from mcp_pfsense.tools import dhcp

from . import sample_data


def test_list_dhcp_leases(client: PfSenseClient) -> None:
    mock_resp = MagicMock()
    mock_resp.json.return_value = sample_data.DHCP_LEASES
    mock_resp.raise_for_status = MagicMock()
    client._client.get.return_value = mock_resp  # type: ignore[union-attr]

    result = dhcp.list_dhcp_leases(client)

    assert len(result) == 2
    assert result[0]["hostname"] == "laptop-home"
    client._client.get.assert_called_once_with(  # type: ignore[union-attr]
        "/status/dhcp_server/leases", params=None
    )


def test_list_dhcp_static_mappings(client: PfSenseClient) -> None:
    mock_resp = MagicMock()
    mock_resp.json.return_value = sample_data.DHCP_STATIC_MAPPINGS
    mock_resp.raise_for_status = MagicMock()
    client._client.get.return_value = mock_resp  # type: ignore[union-attr]

    result = dhcp.list_dhcp_static_mappings(client)

    assert len(result) == 1
    assert result[0]["hostname"] == "nas"


def test_list_dhcp_static_mappings_with_interface(client: PfSenseClient) -> None:
    mock_resp = MagicMock()
    mock_resp.json.return_value = sample_data.DHCP_STATIC_MAPPINGS
    mock_resp.raise_for_status = MagicMock()
    client._client.get.return_value = mock_resp  # type: ignore[union-attr]

    result = dhcp.list_dhcp_static_mappings(client, interface="lan")

    assert len(result) == 1
    # Static mappings are children of the DHCP server, addressed by parent_id
    client._client.get.assert_called_once_with(  # type: ignore[union-attr]
        "/services/dhcp_server/static_mappings", params={"parent_id": "lan"}
    )


def test_add_dhcp_static_mapping(client: PfSenseClient) -> None:
    mock_resp = MagicMock()
    mock_resp.json.return_value = sample_data.DHCP_MAPPING_CREATED
    mock_resp.raise_for_status = MagicMock()
    client._client.post.return_value = mock_resp  # type: ignore[union-attr]

    result = dhcp.add_dhcp_static_mapping(
        client,
        interface="lan",
        mac="aa:bb:cc:dd:ee:20",
        ipaddr="10.10.10.60",
        hostname="printer",
    )

    assert result["id"] == 2
    assert result["hostname"] == "printer"
    client._client.post.assert_called_once_with(  # type: ignore[union-attr]
        "/services/dhcp_server/static_mapping",
        json={
            "parent_id": "lan",
            "apply": True,
            "mac": "aa:bb:cc:dd:ee:20",
            "ipaddr": "10.10.10.60",
            "hostname": "printer",
        },
    )


def test_delete_dhcp_static_mapping_no_confirm(client: PfSenseClient) -> None:
    result = dhcp.delete_dhcp_static_mapping(client, interface="lan", mapping_id=1, confirm=False)

    assert "warning" in result
    assert result["mapping_id"] == 1
    client._client.delete.assert_not_called()  # type: ignore[union-attr]


def test_delete_dhcp_static_mapping_confirmed(client: PfSenseClient) -> None:
    mock_resp = MagicMock()
    mock_resp.json.return_value = sample_data.DHCP_MAPPING_DELETED
    mock_resp.raise_for_status = MagicMock()
    client._client.delete.return_value = mock_resp  # type: ignore[union-attr]

    result = dhcp.delete_dhcp_static_mapping(client, interface="lan", mapping_id=1, confirm=True)

    assert result["success"] is True
    assert result["mapping_id"] == 1
    client._client.delete.assert_called_once_with(  # type: ignore[union-attr]
        "/services/dhcp_server/static_mapping",
        params={"parent_id": "lan", "id": 1, "apply": True},
    )
