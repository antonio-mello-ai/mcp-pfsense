"""Configuration for pfSense MCP server."""

from __future__ import annotations

from pydantic_settings import BaseSettings


class PfSenseConfig(BaseSettings):
    """pfSense connection settings loaded from environment variables."""

    host: str
    username: str = "admin"
    password: str = ""
    port: int = 443
    verify_ssl: bool = False
    scheme: str = "https"

    model_config = {"env_prefix": "PFSENSE_"}

    @classmethod
    def from_env(cls) -> PfSenseConfig:
        """Create config from environment variables."""
        return cls()  # type: ignore[call-arg]

    @property
    def base_url(self) -> str:
        """Build the base URL for the pfSense REST API."""
        return f"{self.scheme}://{self.host}:{self.port}/api/v2"
