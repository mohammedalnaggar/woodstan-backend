"""Structural part generator for lower units.

Lower units have: LS, RS, BT, BK, and — unless corner — STF + STB.
They never have a TP (top panel); stretchers serve that structural role.
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
    """Generate all structural carcass parts for a lower unit.

    Returns parts in order: LS, RS, BT, STF (if not corner), STB (if not
    corner), BK.
    """
    t = profile.carcass_thickness
    bt = profile.back_panel_thickness
    parts: list[Part] = []

    # --- Side panels (LS / RS) -------------------------------------------
    # length = side_height (assembly-method dependent), width = unit.depth
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
                edge_banding=EdgeBanding.front_only(),
                groove=False,
                has_hinges=False,
            )
        )

    # --- Bottom panel (BT) -----------------------------------------------
    if profile.assembly_method is AssemblyMethod.full_sides:
        # BT sits between sides → width = inner_width; length = depth
        bt_length = unit.depth
        bt_width = dims.inner_width
    else:
        # full_top_bottom: BT spans full unit width
        bt_length = unit.depth
        bt_width = unit.width

    parts.append(
        Part(
            id=f"{unit_id}-BT-01",
            unit_id=unit_id,
            role=PartRole.BT,
            length=bt_length,
            width=bt_width,
            thickness=t,
            quantity=1,
            grain_direction="horizontal",
            edge_banding=EdgeBanding.front_only(),
            groove=False,
            has_hinges=False,
        )
    )

    # --- Stretchers (STF / STB) — only non-corner lower units ------------
    if not unit.is_corner:
        # STF: front stretcher — no groove
        parts.append(
            Part(
                id=f"{unit_id}-STF-01",
                unit_id=unit_id,
                role=PartRole.STF,
                length=dims.stretcher_width,
                width=dims.stretcher_depth,
                thickness=t,
                quantity=1,
                grain_direction="horizontal",
                edge_banding=EdgeBanding.front_only(),
                groove=False,
                has_hinges=False,
            )
        )
        # STB: back stretcher — carries the back-panel groove
        parts.append(
            Part(
                id=f"{unit_id}-STB-01",
                unit_id=unit_id,
                role=PartRole.STB,
                length=dims.stretcher_width,
                width=dims.stretcher_depth,
                thickness=t,
                quantity=1,
                grain_direction="horizontal",
                edge_banding=EdgeBanding.none(),
                groove=True,
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
