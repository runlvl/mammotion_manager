"""Application configuration management."""

from __future__ import annotations

import secrets
from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with validation and environment loading."""

    # Server Configuration
    HOST: str = Field(default="0.0.0.0", description="Server bind host")
    PORT: int = Field(default=8000, ge=1, le=65535, description="Server bind port")
    DEBUG: bool = Field(default=False, description="Enable debug mode")
    RELOAD: bool = Field(default=False, description="Enable auto-reload (development)")
    ACCESS_LOG: bool = Field(default=True, description="Enable access logging")

    # Mammotion API Configuration
    REGION: str = Field(default="eu", description="Mammotion API region")
    COUNTRY_CODE: str = Field(default="DE", description="ISO country code for region discovery")

    # Security Configuration
    SECRET_KEY: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        description="Secret key for session signing and encryption"
    )
    SESSION_EXPIRE_HOURS: int = Field(
        default=24, ge=1, le=168, description="Session expiration time in hours"
    )
    CORS_ORIGINS: List[str] = Field(
        default_factory=list, description="Allowed CORS origins"
    )

    # Redis Configuration
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0", description="Redis connection URL"
    )
    REDIS_PASSWORD: Optional[str] = Field(default=None, description="Redis password")
    REDIS_SSL: bool = Field(default=False, description="Use SSL for Redis connection")

    # Logging Configuration
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(default="json", description="Log format (json|text)")
    LOG_FILE: Optional[Path] = Field(default=None, description="Log file path")

    # Feature Configuration
    ENABLE_METRICS: bool = Field(default=True, description="Enable metrics collection")
    ENABLE_HEALTH_CHECKS: bool = Field(default=True, description="Enable health check endpoints")
    STATUS_POLL_INTERVAL: int = Field(
        default=15, ge=5, le=300, description="Device status polling interval in seconds"
    )

    # Directory Configuration
    BASE_DIR: Path = Field(default_factory=lambda: Path(__file__).resolve().parent)
    STATIC_DIR: Path = Field(default_factory=lambda: Path(__file__).resolve().parent / "static")
    TEMPLATES_DIR: Path = Field(default_factory=lambda: Path(__file__).resolve().parent / "templates")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of: {', '.join(valid_levels)}")
        return v.upper()

    @field_validator("LOG_FORMAT")
    @classmethod
    def validate_log_format(cls, v: str) -> str:
        """Validate log format."""
        valid_formats = {"json", "text"}
        if v.lower() not in valid_formats:
            raise ValueError(f"LOG_FORMAT must be one of: {', '.join(valid_formats)}")
        return v.lower()

    @field_validator("REGION")
    @classmethod
    def validate_region(cls, v: str) -> str:
        """Validate Mammotion region."""
        valid_regions = {"eu", "us", "asia"}
        if v.lower() not in valid_regions:
            raise ValueError(f"REGION must be one of: {', '.join(valid_regions)}")
        return v.lower()

    @field_validator("COUNTRY_CODE")
    @classmethod
    def validate_country_code(cls, v: str) -> str:
        """Validate ISO country code."""
        if len(v) != 2 or not v.isalpha():
            raise ValueError("COUNTRY_CODE must be a 2-letter ISO country code")
        return v.upper()

    def get_redis_config(self) -> dict:
        """Get Redis configuration dictionary."""
        config = {
            "url": self.REDIS_URL,
            "decode_responses": True,
            "socket_connect_timeout": 5,
            "socket_timeout": 5,
            "retry_on_timeout": True,
        }
        
        if self.REDIS_PASSWORD:
            config["password"] = self.REDIS_PASSWORD
        
        if self.REDIS_SSL:
            config["ssl"] = True
            config["ssl_cert_reqs"] = None
        
        return config


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()
