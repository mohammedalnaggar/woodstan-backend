"""Dimension resolver for the ``full_sides`` assembly method.

In full_sides assembly the side panels run the full external height of the
unit, so the top and bottom panels sit *between* the sides.

    inner_width  = W - 2 * T          (T = carcass_thickness)
    inner_height = H - 2 * T
    side_height  = H                  (sides span full external height)

All other derived dimensions follow from inner_width / inner_height.
"""

from __future__ import annotations

# Back-panel groove dimensions (cm): 8 mm wide × 8 mm deep, 19 mm from edge
_GROOVE_DEPTH_CM: float = 0.8
_STRETCHER_DEPTH_CM: float = 10.0
_BACK_ALLOWANCE_CM: float = 3.0
_SHELF_CLEARANCE_CM: float = 0.1

from engine.models.profile import WorkshopProfile
from engine.models.result import DimensionSet
from engine.models.unit import UnitDefinition


def resolve_dimensions(unit: UnitDefinition, profile: WorkshopProfile) -> DimensionSet:
    """Return pre-computed interior dimensions for a *full_sides* unit.

    Args:
        unit:    The cabinet specification (width, height, depth in cm).
        profile: Workshop settings supplying material thicknesses.

    Returns:
        A fully-populated :class:`DimensionSet`; all values in cm.
    """
    t = profile.carcass_thickness

    inner_width = unit.width - 2 * t
    inner_height = unit.height - 2 * t
    side_height = unit.height  # sides cover top + bottom in full_sides

    return DimensionSet(
        inner_width=inner_width,
        inner_height=inner_height,
        side_height=side_height,
        shelf_width=inner_width - _SHELF_CLEARANCE_CM,
        shelf_depth=unit.depth - _BACK_ALLOWANCE_CM,
        back_panel_width=inner_width + 2 * _GROOVE_DEPTH_CM,
        back_panel_height=inner_height + 2 * _GROOVE_DEPTH_CM,
        stretcher_width=inner_width,
        stretcher_depth=_STRETCHER_DEPTH_CM,
    )
