"""Result types — successful engine output."""

from __future__ import annotations

from dataclasses import dataclass

from engine.models.part import Part
from engine.models.unit import UnitType

__all__ = ["DimensionSet", "GeneratedUnit"]


@dataclass(frozen=True)
class DimensionSet:
    """Pre-computed interior dimensions for a unit.

    Produced by the resolver for the active assembly method and
    consumed by generators and validators.  All values in cm.

    side_height:
        Height of the side panels.
        full_sides    → unit.height  (sides cover top + bottom)
        full_top_bottom → inner_height  (sides sit between top + bottom)
    """

    inner_width: float          # horizontal interior clearance
    inner_height: float         # vertical interior clearance
    side_height: float          # side panel height (assembly-method dependent)
    shelf_width: float          # inner_width − 0.1 cm clearance
    shelf_depth: float          # unit.depth − 3.0 cm back allowance
    back_panel_width: float     # inner_width  + 2 × groove_depth
    back_panel_height: float    # inner_height + 2 × groove_depth
    stretcher_width: float      # inner_width (lower units)
    stretcher_depth: float      # 10.0 cm fixed


@dataclass(frozen=True)
class GeneratedUnit:
    """Successful output of a single engine call.

    parts is a tuple to enforce immutability.  Parts are ordered:
    structural panels → shelves → drawers.
    """

    unit_id: str
    unit_type: UnitType
    parts: tuple[Part, ...]
