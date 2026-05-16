"""Validation error model and named rule constants.

Rule name strings are stable identifiers — changing a constant value
is a breaking change that requires a version bump.

Tests MUST assert on the constant values, not on the human-readable
message field, so that message wording can be improved without
breaking tests.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "ValidationError",
    "RULE_SHELF_SPAN",
    "RULE_DRAWER_NOT_PERMITTED",
    "RULE_DRAWER_WIDTH_CLEARANCE",
    "RULE_PART_BELOW_MIN",
    "RULE_PART_ABOVE_MAX",
    "RULE_STRETCHER_MISSING",
    "RULE_STRETCHER_ON_CORNER",
]

# ---------------------------------------------------------------------------
# Named rule constants — stable identifiers used in tests and API responses
# ---------------------------------------------------------------------------

RULE_SHELF_SPAN = "shelf_span_exceeded"
RULE_DRAWER_NOT_PERMITTED = "drawer_not_permitted"
RULE_DRAWER_WIDTH_CLEARANCE = "drawer_width_clearance"
RULE_PART_BELOW_MIN = "part_below_min_dimension"
RULE_PART_ABOVE_MAX = "part_above_max_dimension"
RULE_STRETCHER_MISSING = "stretcher_missing"
RULE_STRETCHER_ON_CORNER = "stretcher_on_corner"


@dataclass(frozen=True)
class ValidationError:
    """A single manufacturability rule violation.

    Attributes:
        rule:            Machine-readable rule name (one of the RULE_* constants).
        offending_value: The submitted or computed value that failed (cm).
        limit:           The allowed threshold or boundary (cm).
        message:         Human-readable description for logging and UI display.
                         Do NOT assert on this field in tests.
    """

    rule: str
    offending_value: float
    limit: float
    message: str
