from __future__ import annotations

import logging
from typing import Optional

try:
    import keyring  # type: ignore
except Exception as e:  # pragma: no cover
    keyring = None

logger = logging.getLogger(__name__)


class KeyringUnavailableError(RuntimeError):
    pass


class KeyringStore:
    """Thin wrapper to store/retrieve tokens securely via keyring.

    We never store raw passwords. Only access/refresh tokens returned by PyMammotion.
    """

    def __init__(self, service_name: str = "mammotion-web") -> None:
        self.service_name = service_name
        if keyring is None:
            raise KeyringUnavailableError("python-keyring backend is not available")

    def set_token(self, username: str, token: str) -> None:
        if not token:
            raise ValueError("Empty token not allowed")
        keyring.set_password(self.service_name, username, token)  # type: ignore[attr-defined]

    def get_token(self, username: str) -> Optional[str]:
        return keyring.get_password(self.service_name, username)  # type: ignore[attr-defined]

    def delete_token(self, username: str) -> None:
        try:
            keyring.delete_password(self.service_name, username)  # type: ignore[attr-defined]
        except Exception:
            # Ignore if missing
            pass
