"""Pending-changes (apply) tools.

pfSense stages configuration writes: a firewall rule, DHCP static mapping or
DNS host override is stored in the config but does nothing until its
subsystem is applied ("Apply Changes" in the WebGUI). The write tools follow
the same model — they stage by default — and these tools inspect and apply
what is pending. Applying reloads the whole subsystem, which also activates
anything a human left staged in the WebGUI, so it is gated by `confirm`.
"""

from __future__ import annotations

from typing import Any

from mcp_pfsense.client import PfSenseClient

SUBSYSTEMS = ("firewall", "dhcp", "dns")


def with_apply_state(payload: dict[str, Any], subsystem: str, applied: bool) -> dict[str, Any]:
    """Annotate a write result with whether the change is live or still pending."""
    payload["applied"] = applied
    if not applied:
        payload["pending"] = (
            f"Staged in the pfSense config but not active yet. Call "
            f"apply_changes(subsystem='{subsystem}', confirm=true) to apply, or apply it in "
            f"the pfSense WebGUI."
        )
    return payload


def _check_subsystem(subsystem: str) -> None:
    if subsystem not in SUBSYSTEMS:
        raise ValueError(
            f"Unknown subsystem '{subsystem}'. Expected one of: {', '.join(SUBSYSTEMS)}."
        )


def get_pending_changes(client: PfSenseClient, subsystem: str) -> dict[str, Any]:
    """Report whether a subsystem (firewall, dhcp, dns) has staged changes waiting to be applied."""
    _check_subsystem(subsystem)
    result = client.get_apply_status(subsystem)
    data: dict[str, Any] = result.get("data", result)
    return {"subsystem": subsystem, **data}


def apply_changes(
    client: PfSenseClient,
    subsystem: str,
    confirm: bool = False,
) -> dict[str, Any]:
    """Apply the staged changes of a subsystem (firewall, dhcp, dns). Requires confirm=true."""
    _check_subsystem(subsystem)
    if not confirm:
        return {
            "warning": f"This will apply ALL pending {subsystem} changes on the firewall — "
            f"including any a human staged in the WebGUI and has not reviewed yet. "
            f"Call again with confirm=true to proceed.",
            "subsystem": subsystem,
        }

    result = client.apply_changes(subsystem)
    return {
        "success": True,
        "subsystem": subsystem,
        "message": f"Pending {subsystem} changes applied.",
        "data": result.get("data", {}),
    }
