"""Drawer box generator.

For each DrawerConfig the engine produces five parts:
    DD  — drawer door/external front (full inner_width × drawer_height)
    DSL — depth panel left  (fixed 45 cm depth)
    DSR — depth panel right
    DWF — width panel front (inner_width after clearance)
    DWB — width panel back

Drawer height is determined by dividing inner_height equally among all
drawers (simplified Phase-1 approach; Phase 2 may support custom heights).

Slide clearance deducted from drawer body width:
    side_slides   → 2.5 cm total
    bottom_slides → 0.6 cm total

All drawer parts use carcass_thickness from the workshop profile.
"""

from __future__ import annotations

from engine.models.part import EdgeBanding, Part, PartRole
from engine.models.profile import WorkshopProfile
from engine.models.result import DimensionSet
from engine.models.unit import DrawerSlideType, UnitDefinition

_DRAWER_DEPTH_CM: float = 45.0       # industry-standard drawer depth
_SIDE_SLIDE_CLEARANCE_CM: float = 2.5
_BOTTOM_SLIDE_CLEARANCE_CM: float = 0.6


def generate_drawers(
    unit_id: str,
    unit: UnitDefinition,
    dims: DimensionSet,
    profile: WorkshopProfile,
) -> list[Part]:
    """Generate all drawer box components for the unit.

    Returns an empty list when the unit has no drawers.
    """
    if not unit.drawers:
        return []

    t = profile.carcass_thickness
    drawer_count = len(unit.drawers)
    drawer_height = dims.inner_height / drawer_count

    parts: list[Part] = []

    for drawer in unit.drawers:
        seq = drawer.position
        if drawer.slide_type is DrawerSlideType.side_slides:
            clearance = _SIDE_SLIDE_CLEARANCE_CM
        else:
            clearance = _BOTTOM_SLIDE_CLEARANCE_CM

        body_width = dims.inner_width - clearance

        # Drawer door (external front): spans full inner_width
        parts.append(
            Part(
                id=f"{unit_id}-DD-{seq:02d}",
                unit_id=unit_id,
                role=PartRole.DD,
                length=drawer_height,
                width=dims.inner_width,
                thickness=t,
                quantity=1,
                grain_direction="vertical",
                edge_banding=EdgeBanding.all_four(),
                groove=False,
                has_hinges=False,
            )
        )

        # Depth panels (DSL / DSR) — perpendicular to door
        for role, label in [(PartRole.DSL, "DSL"), (PartRole.DSR, "DSR")]:
            parts.append(
                Part(
                    id=f"{unit_id}-{label}-{seq:02d}",
                    unit_id=unit_id,
                    role=role,
                    length=_DRAWER_DEPTH_CM,
                    width=drawer_height,
                    thickness=t,
                    quantity=1,
                    grain_direction="horizontal",
                    edge_banding=EdgeBanding.none(),
                    groove=False,
                    has_hinges=False,
                )
            )

        # Width panels (DWF front / DWB back) — parallel to door
        for role, label in [(PartRole.DWF, "DWF"), (PartRole.DWB, "DWB")]:
            parts.append(
                Part(
                    id=f"{unit_id}-{label}-{seq:02d}",
                    unit_id=unit_id,
                    role=role,
                    length=body_width,
                    width=drawer_height,
                    thickness=t,
                    quantity=1,
                    grain_direction="horizontal",
                    edge_banding=EdgeBanding.none(),
                    groove=False,
                    has_hinges=False,
                )
            )

    return parts
