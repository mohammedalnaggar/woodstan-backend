"""Tests that engine output is fully deterministic (same input → same output)."""

from engine import generate_unit
from engine.models.profile import AssemblyMethod, WorkshopProfile
from engine.models.result import GeneratedUnit
from engine.models.room import RoomContext
from engine.models.unit import UnitDefinition, UnitType


def _profile():
    return WorkshopProfile(
        assembly_method=AssemblyMethod.full_sides,
        carcass_thickness=1.855,
        back_panel_thickness=0.7,
        edge_banding_thickness=0.1,
    )


def _unit():
    return UnitDefinition(
        unit_type=UnitType.lower,
        width=60.0, height=72.0, depth=58.0,
        shelf_count=2,
    )


class TestDeterminism:
    def test_ten_runs_identical(self):
        """T038 — 10 consecutive runs with identical inputs must produce identical output."""
        profile = _profile()
        unit = _unit()
        room = RoomContext()

        first, first_errors = generate_unit(unit, profile, room)
        for _ in range(9):
            subsequent, subsequent_errors = generate_unit(unit, profile, room)
            assert subsequent == first
            assert subsequent_errors == first_errors
            for p1, p2 in zip(first.parts, subsequent.parts):
                assert p1 == p2

    def test_same_input_same_output(self):
        profile = _profile()
        unit = _unit()
        room = RoomContext()

        g1, e1 = generate_unit(unit, profile, room)
        g2, e2 = generate_unit(unit, profile, room)

        assert g1 == g2
        assert e1 == e2

    def test_same_parts_in_same_order(self):
        profile = _profile()
        unit = _unit()
        room = RoomContext()

        g1, _ = generate_unit(unit, profile, room)
        g2, _ = generate_unit(unit, profile, room)

        for p1, p2 in zip(g1.parts, g2.parts):
            assert p1 == p2

    def test_unit_id_depends_on_room(self):
        profile = _profile()
        unit = _unit()

        empty_room = RoomContext()
        populated_room = RoomContext(existing_unit_ids=("CAB-001", "CAB-002"))

        g_empty, _ = generate_unit(unit, profile, empty_room)
        g_populated, _ = generate_unit(unit, profile, populated_room)

        assert g_empty.unit_id == "CAB-001"
        assert g_populated.unit_id == "CAB-003"

    def test_generated_unit_is_frozen(self):
        """GeneratedUnit and its parts must be immutable (frozen dataclasses)."""
        profile = _profile()
        unit = _unit()
        room = RoomContext()

        generated, _ = generate_unit(unit, profile, room)

        import pytest
        with pytest.raises((AttributeError, TypeError)):
            generated.unit_id = "MUTATED"  # type: ignore[misc]
