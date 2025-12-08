"""Convenience import for anti-spoonfeed safety checks."""

from backend.integrations.safety.anti_spoonfeed import (
    check_spoonfeeding_risk,
    is_spoonfeeding,
)

__all__ = ["check_spoonfeeding_risk", "is_spoonfeeding"]
