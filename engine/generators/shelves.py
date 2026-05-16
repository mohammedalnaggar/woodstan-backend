"""Adjustable shelf generator.

Shelves are sequenced SH-01, SH-02, … based on ``unit.shelf_count``.
Each shelf is identical in dimensions and has no edge banding by default
(finished edges are optional site-fitted detail, not cut-list required).
"""

from __future__ import annotations

from engine.models.part import EdgeBanding, Part, PartRole
from engine.models.profile import WorkshopProfile
from engine.models.result import DimensionSet
from engine.models.unit import UnitDefinition


def generate_shelves(
    unit_id: str,
    unit: UnitDefinition,
    dims: DimensionSet,
    profile: WorkshopProfile,
) -> list[Part]:
    """Generate all adjustable shelf panels for the unit.

    Returns an empty list when ``unit.shelf_count == 0``.
    """
    t = profile.carcass_thickness
    parts: list[Part] = []

    for seq in range(1, unit.shelf_count + 1):
        parts.append(
            Part(
                id=f"{unit_id}-SH-{seq:02d}",
                unit_id=unit_id,
                role=PartRole.SH,
                length=dims.shelf_depth,
                width=dims.shelf_width,
                thickness=t,
                quantity=1,
                grain_direction="horizontal",
                edge_banding=EdgeBanding.front_only(),
                groove=False,
                has_hinges=False,
            )
        )

    return parts
