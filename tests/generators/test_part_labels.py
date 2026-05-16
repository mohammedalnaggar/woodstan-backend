"""T039 + T040 — Part ID format and sequential label tests.

Verifies the schema: [UNIT_ID]-[PART_ROLE]-[SEQUENCE]
and that sequences for multi-part roles (SH, DD, DSL …) are gap-free.
"""

import pytest

from engine import generate_unit
from engine.models.profile import AssemblyMethod, WorkshopProfile
from engine.models.room import RoomContext
from engine.models.unit import DrawerConfig, DrawerSlideType, UnitDefinition, UnitType


@pytest.fixture
def profile():
    return WorkshopProfile(
        assembly_method=AssemblyMethod.full_sides,
        carcass_thickness=1.855,
        back_panel_thickness=0.7,
        edge_banding_thickness=0.1,
    )


class TestPartIdFormat:
    """T039 — exact ID strings for a standard lower unit."""

    def test_left_side_id(self, profile):
        unit = UnitDefinition(
            unit_type=UnitType.lower,
            width=60.0, height=72.0, depth=58.0,
            shelf_count=0,
        )
        generated, _ = generate_unit(unit, profile, RoomContext())
        ids = {p.id for p in generated.parts}
        assert "CAB-001-LS-01" in ids

    def test_right_side_id(self, profile):
        unit = UnitDefinition(
            unit_type=UnitType.lower,
            width=60.0, height=72.0, depth=58.0,
            shelf_count=0,
        )
        generated, _ = generate_unit(unit, profile, RoomContext())
        ids = {p.id for p in generated.parts}
        assert "CAB-001-RS-01" in ids

    def test_front_stretcher_id(self, profile):
        unit = UnitDefinition(
            unit_type=UnitType.lower,
            width=60.0, height=72.0, depth=58.0,
            shelf_count=0,
        )
        generated, _ = generate_unit(unit, profile, RoomContext())
        ids = {p.id for p in generated.parts}
        assert "CAB-001-STF-01" in ids

    def test_back_stretcher_id(self, profile):
        unit = UnitDefinition(
            unit_type=UnitType.lower,
            width=60.0, height=72.0, depth=58.0,
            shelf_count=0,
        )
        generated, _ = generate_unit(unit, profile, RoomContext())
        ids = {p.id for p in generated.parts}
        assert "CAB-001-STB-01" in ids

    def test_back_panel_id(self, profile):
        unit = UnitDefinition(
            unit_type=UnitType.lower,
            width=60.0, height=72.0, depth=58.0,
            shelf_count=0,
        )
        generated, _ = generate_unit(unit, profile, RoomContext())
        ids = {p.id for p in generated.parts}
        assert "CAB-001-BK-01" in ids

    def test_unit_id_in_all_part_ids(self, profile):
        room = RoomContext(existing_unit_ids=("CAB-001", "CAB-002"))
        unit = UnitDefinition(
            unit_type=UnitType.lower,
            width=60.0, height=72.0, depth=58.0,
            shelf_count=0,
        )
        generated, _ = generate_unit(unit, profile, room)
        assert generated.unit_id == "CAB-003"
        for p in generated.parts:
            assert p.id.startswith("CAB-003-")
            assert p.unit_id == "CAB-003"


class TestSequentialLabels:
    """T040 — gap-free sequential numbering for shelves and drawer components."""

    def test_three_shelves_sequential(self, profile):
        unit = UnitDefinition(
            unit_type=UnitType.lower,
            width=60.0, height=72.0, depth=58.0,
            shelf_count=3,
        )
        generated, _ = generate_unit(unit, profile, RoomContext())
        ids = {p.id for p in generated.parts}
        assert "CAB-001-SH-01" in ids
        assert "CAB-001-SH-02" in ids
        assert "CAB-001-SH-03" in ids
        # No gaps
        assert "CAB-001-SH-04" not in ids

    def test_two_drawers_sequential_dd(self, profile):
        d1 = DrawerConfig(position=1, slide_type=DrawerSlideType.side_slides)
        d2 = DrawerConfig(position=2, slide_type=DrawerSlideType.side_slides)
        unit = UnitDefinition(
            unit_type=UnitType.lower,
            width=60.0, height=72.0, depth=58.0,
            shelf_count=0,
            drawers=(d1, d2),
        )
        generated, _ = generate_unit(unit, profile, RoomContext())
        ids = {p.id for p in generated.parts}
        assert "CAB-001-DD-01" in ids
        assert "CAB-001-DD-02" in ids

    def test_two_drawers_sequential_depth_panels(self, profile):
        d1 = DrawerConfig(position=1, slide_type=DrawerSlideType.side_slides)
        d2 = DrawerConfig(position=2, slide_type=DrawerSlideType.side_slides)
        unit = UnitDefinition(
            unit_type=UnitType.lower,
            width=60.0, height=72.0, depth=58.0,
            shelf_count=0,
            drawers=(d1, d2),
        )
        generated, _ = generate_unit(unit, profile, RoomContext())
        ids = {p.id for p in generated.parts}
        for role in ("DSL", "DSR", "DWF", "DWB"):
            assert f"CAB-001-{role}-01" in ids
            assert f"CAB-001-{role}-02" in ids

    def test_zero_shelves_no_sh_parts(self, profile):
        unit = UnitDefinition(
            unit_type=UnitType.lower,
            width=60.0, height=72.0, depth=58.0,
            shelf_count=0,
        )
        generated, _ = generate_unit(unit, profile, RoomContext())
        ids = {p.id for p in generated.parts}
        assert not any("SH" in pid for pid in ids)
