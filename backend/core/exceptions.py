from __future__ import annotations

from email import message
from typing import Any

class EquilibriaError(Exception):
    """Base exception for all Equilibria domain/simulation errors."""

    def __init__(self, message: str, context: dict[str, Any] | None = None):
        super().__init__(message)
        self.message = message
        self.context: dict[str, Any] = context or {}

    def __str__(self) -> str:
        if not self.context:
            return self.message
        return f"{self.message}: {self.context}"


class DomainValidationError(EquilibriaError):
    """Raised when user/domain inputs violate invariants."""

class ThermodynamicError(EquilibriaError):
    """Raised when CoolProp/thermo property evaluation fails."""

class BalanceError(EquilibriaError):
    """Raised when unit op or flowsheet balance fails to close."""