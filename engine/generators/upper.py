"""Structural part generator for upper units (mid_upper and high_upper).

Upper units have: LS, RS, TP, BT, BK.
They never have stretchers.
"""

from __future__ import annotations

from engine.models.part import EdgeBanding, Part, PartRole
from engine.models.profile import AssemblyMethod, WorkshopProfile
from engine.models.result import DimensionSet
from engine.models.unit import UnitDefinition


def generate_structural(
    unit_id: str,
    unit: UnitDefinition,
    dims: DimensionSet,
    profile: WorkshopProfile,
) -> list[Part]:
    """Generate all structural carcass parts for an upper unit.

    Returns parts in order: LS, RS, TP, BT, BK.
    """
    t = profile.carcass_thickness
    bt = profile.back_panel_thickness
    parts: list[Part] = []

    # --- Side panels (LS / RS) -------------------------------------------
    for role, label in [(PartRole.LS, "LS"), (PartRole.RS, "RS")]:
        parts.append(
            Part(
                id=f"{unit_id}-{label}-01",
                unit_id=unit_id,
                role=role,
                length=dims.side_height,
                width=unit.depth,
                thickness=t,
                quantity=1,
                grain_direction="vertical",
                edge_banding=EdgeBanding.upper_side(),
                groove=False,
                has_hinges=False,
            )
        )

    # --- Top + Bottom panels (TP / BT) -----------------------------------
    if profile.assembly_method is AssemblyMethod.full_sides:
        # TP/BT sit between sides → width = inner_width
        horiz_width = dims.inner_width
    else:
        # full_top_bottom: panels span full unit width
        horiz_width = unit.width

    for role, label in [(PartRole.TP, "TP"), (PartRole.BT, "BT")]:
        parts.append(
            Part(
                id=f"{unit_id}-{label}-01",
                unit_id=unit_id,
                role=role,
                length=unit.depth,
                width=horiz_width,
                thickness=t,
                quantity=1,
                grain_direction="horizontal",
                edge_banding=EdgeBanding.front_only(),
                groove=False,
                has_hinges=False,
            )
        )

    # --- Back panel (BK) -------------------------------------------------
    parts.append(
        Part(
            id=f"{unit_id}-BK-01",
            unit_id=unit_id,
            role=PartRole.BK,
            length=dims.back_panel_height,
            width=dims.back_panel_width,
            thickness=bt,
            quantity=1,
            grain_direction="vertical",
            edge_banding=EdgeBanding.none(),
            groove=False,
            has_hinges=False,
        )
    )

    return parts
