"""Individual validation rule functions.

Each function inspects one specific constraint and returns a
:class:`ValidationError` when violated, or ``None`` when the unit passes.

Rule names are the stable ``RULE_*`` constants from ``engine.models.errors``.
Tests MUST assert on those constants, not on the ``message`` field.
"""

from __future__ import annotations

from typing import Optional

from engine.models.errors import (
    RULE_DRAWER_NOT_PERMITTED,
    RULE_DRAWER_WIDTH_CLEARANCE,
    RULE_PART_ABOVE_MAX,
    RULE_PART_BELOW_MIN,
    RULE_SHELF_SPAN,
    RULE_STRETCHER_MISSING,
    RULE_STRETCHER_ON_CORNER,
    ValidationError,
)
from engine.models.result import DimensionSet
from engine.models.unit import DrawerSlideType, UnitDefinition, UnitType

# ---------------------------------------------------------------------------
# Manufacturing dimension limits (cm)
# ---------------------------------------------------------------------------
_MAX_SHELF_SPAN_CM: float = 90.0   # beyond this, shelf sags under load
_MIN_PART_CM: float = 5.0          # CNC minimum cutting dimension
_MAX_PART_CM: float = 300.0        # sheet-goods practical maximum

# Drawer slide clearances (cm)
_SIDE_SLIDE_CLEARANCE_CM: float = 2.5   # 25 mm total (both sides)
_BOTTOM_SLIDE_CLEARANCE_CM: float = 0.6  # 6 mm


def check_shelf_span(
    unit: UnitDefinition, dims: DimensionSet
) -> Optional[ValidationError]:
    """Shelf span must not exceed the sag limit."""
    if dims.shelf_width > _MAX_SHELF_SPAN_CM:
        return ValidationError(
            rule=RULE_SHELF_SPAN,
            offending_value=round(dims.shelf_width, 4),
            limit=_MAX_SHELF_SPAN_CM,
            message=(
                f"Shelf span {dims.shelf_width:.2f} cm exceeds the "
                f"{_MAX_SHELF_SPAN_CM:.0f} cm sag limit."
            ),
        )
    return None


def check_drawer_not_permitted(unit: UnitDefinition) -> Optional[ValidationError]:
    """Drawers are only valid for lower units."""
    if unit.drawers and unit.unit_type != UnitType.lower:
        return ValidationError(
            rule=RULE_DRAWER_NOT_PERMITTED,
            offending_value=float(len(unit.drawers)),
            limit=0.0,
            message=(
                f"Drawers are not permitted for {unit.unit_type.value!r} units."
            ),
        )
    return None


def check_drawer_width_clearance(
    unit: UnitDefinition, dims: DimensionSet
) -> Optional[ValidationError]:
    """Drawer body must fit inside the unit after slide clearance is deducted."""
    for drawer in unit.drawers:
        if drawer.slide_type is DrawerSlideType.side_slides:
            clearance = _SIDE_SLIDE_CLEARANCE_CM
        else:
            clearance = _BOTTOM_SLIDE_CLEARANCE_CM

        drawer_body_width = dims.inner_width - clearance
        if drawer_body_width < _MIN_PART_CM:
            return ValidationError(
                rule=RULE_DRAWER_WIDTH_CLEARANCE,
                offending_value=round(drawer_body_width, 4),
                limit=_MIN_PART_CM,
                message=(
                    f"Drawer body width {drawer_body_width:.2f} cm after "
                    f"{clearance:.1f} cm slide clearance is below the "
                    f"{_MIN_PART_CM:.0f} cm minimum."
                ),
            )
    return None


def check_part_below_min(dims: DimensionSet) -> Optional[ValidationError]:
    """No computed panel dimension may fall below the CNC minimum."""
    checks = {
        "inner_width": dims.inner_width,
        "inner_height": dims.inner_height,
        "shelf_width": dims.shelf_width,
        "shelf_depth": dims.shelf_depth,
        "back_panel_width": dims.back_panel_width,
        "back_panel_height": dims.back_panel_height,
    }
    for name, value in checks.items():
        if value < _MIN_PART_CM:
            return ValidationError(
                rule=RULE_PART_BELOW_MIN,
                offending_value=round(value, 4),
                limit=_MIN_PART_CM,
                message=(
                    f"Computed dimension '{name}' = {value:.2f} cm is below "
                    f"the {_MIN_PART_CM:.0f} cm minimum part size."
                ),
            )
    return None


def check_part_above_max(dims: DimensionSet) -> Optional[ValidationError]:
    """No computed panel dimension may exceed the sheet-goods practical maximum."""
    checks = {
        "inner_width": dims.inner_width,
        "inner_height": dims.inner_height,
        "back_panel_width": dims.back_panel_width,
        "back_panel_height": dims.back_panel_height,
        "side_height": dims.side_height,
    }
    for name, value in checks.items():
        if value > _MAX_PART_CM:
            return ValidationError(
                rule=RULE_PART_ABOVE_MAX,
                offending_value=round(value, 4),
                limit=_MAX_PART_CM,
                message=(
                    f"Computed dimension '{name}' = {value:.2f} cm exceeds "
                    f"the {_MAX_PART_CM:.0f} cm maximum part size."
                ),
            )
    return None


def check_stretcher_missing(
    unit: UnitDefinition, parts_roles: frozenset[str]
) -> Optional[ValidationError]:
    """Lower non-corner units must have both STF and STB stretchers."""
    if unit.unit_type is not UnitType.lower or unit.is_corner:
        return None
    missing = {"STF", "STB"} - parts_roles
    if missing:
        return ValidationError(
            rule=RULE_STRETCHER_MISSING,
            offending_value=0.0,
            limit=1.0,
            message=(
                f"Lower non-corner unit is missing stretcher role(s): "
                f"{', '.join(sorted(missing))}."
            ),
        )
    return None


def check_stretcher_on_corner(
    unit: UnitDefinition, parts_roles: frozenset[str]
) -> Optional[ValidationError]:
    """Corner lower units must NOT have stretchers."""
    if unit.unit_type is not UnitType.lower or not unit.is_corner:
        return None
    present = {"STF", "STB"} & parts_roles
    if present:
        return ValidationError(
            rule=RULE_STRETCHER_ON_CORNER,
            offending_value=float(len(present)),
            limit=0.0,
            message=(
                f"Corner lower unit must not have stretchers; "
                f"found: {', '.join(sorted(present))}."
            ),
        )
    return None
