"""T041 — Corner unit tests: lower and upper, with and without is_corner."""

import pytest

from engine import generate_unit
from engine.models.errors import RULE_STRETCHER_MISSING, RULE_STRETCHER_ON_CORNER
from engine.models.part import PartRole
from engine.models.profile import AssemblyMethod, WorkshopProfile
from engine.models.room import RoomContext
from engine.models.unit import UnitDefinition, UnitType
from engine.generators.lower import generate_structural
from engine.resolvers.base import resolve_dimensions


@pytest.fixture
def profile():
    return WorkshopProfile(
        assembly_method=AssemblyMethod.full_sides,
        carcass_thickness=1.855,
        back_panel_thickness=0.7,
        edge_banding_thickness=0.1,
    )


class TestLowerCornerUnit:
    def test_no_stf_or_stb_parts(self, profile):
        unit = UnitDefinition(
            unit_type=UnitType.lower,
            width=90.0, height=72.0, depth=58.0,
            shelf_count=0,
            is_corner=True,
        )
        generated, _ = generate_unit(unit, profile, RoomContext())
        roles = {p.role for p in generated.parts}
        assert PartRole.STF not in roles
        assert PartRole.STB not in roles

    def test_stretcher_missing_rule_not_triggered(self, profile):
        unit = UnitDefinition(
            unit_type=UnitType.lower,
            width=90.0, height=72.0, depth=58.0,
            shelf_count=0,
            is_corner=True,
        )
        generated, errors = generate_unit(unit, profile, RoomContext())
        rule_names = {e.rule for e in errors}
        assert RULE_STRETCHER_MISSING not in rule_names

    def test_stretcher_on_corner_rule_not_triggered(self, profile):
        """The corner unit should not have stretchers, so this rule is silent."""
        unit = UnitDefinition(
            unit_type=UnitType.lower,
            width=90.0, height=72.0, depth=58.0,
            shelf_count=0,
            is_corner=True,
        )
        generated, errors = generate_unit(unit, profile, RoomContext())
        rule_names = {e.rule for e in errors}
        assert RULE_STRETCHER_ON_CORNER not in rule_names

    def test_corner_lower_still_has_ls_rs_bt_bk(self, profile):
        unit = UnitDefinition(
            unit_type=UnitType.lower,
            width=90.0, height=72.0, depth=58.0,
            shelf_count=0,
            is_corner=True,
        )
        generated, _ = generate_unit(unit, profile, RoomContext())
        roles = {p.role for p in generated.parts}
        assert {PartRole.LS, PartRole.RS, PartRole.BT, PartRole.BK}.issubset(roles)


class TestUpperCornerUnit:
    def test_mid_upper_corner_identical_carcass_to_non_corner(self, profile):
        """is_corner has no carcass effect for upper units in Phase 1."""
        unit_std = UnitDefinition(
            unit_type=UnitType.mid_upper,
            width=60.0, height=60.0, depth=35.0,
            shelf_count=0,
            is_corner=False,
        )
        unit_corner = UnitDefinition(
            unit_type=UnitType.mid_upper,
            width=60.0, height=60.0, depth=35.0,
            shelf_count=0,
            is_corner=True,
        )
        room = RoomContext()
        gen_std, _ = generate_unit(unit_std, profile, room)
        gen_corner, _ = generate_unit(unit_corner, profile, room)

        # Same number and type of parts
        roles_std = sorted(p.role.value for p in gen_std.parts)
        roles_corner = sorted(p.role.value for p in gen_corner.parts)
        assert roles_std == roles_corner

        # Same dimensions (ignoring unit_id)
        for ps, pc in zip(
            sorted(gen_std.parts, key=lambda p: p.role.value),
            sorted(gen_corner.parts, key=lambda p: p.role.value),
        ):
            assert ps.length == pytest.approx(pc.length, rel=1e-6)
            assert ps.width == pytest.approx(pc.width, rel=1e-6)

    def test_upper_corner_no_stretchers(self, profile):
        unit = UnitDefinition(
            unit_type=UnitType.high_upper,
            width=60.0, height=90.0, depth=35.0,
            shelf_count=0,
            is_corner=True,
        )
        generated, _ = generate_unit(unit, profile, RoomContext())
        roles = {p.role for p in generated.parts}
        assert PartRole.STF not in roles
        assert PartRole.STB not in roles

    def test_face_width_none_accepted_without_error(self, profile):
        """face_width_l/r = None is valid in Phase 1 — no error raised."""
        unit = UnitDefinition(
            unit_type=UnitType.mid_upper,
            width=60.0, height=60.0, depth=35.0,
            shelf_count=0,
            is_corner=True,
            face_width_l=None,
            face_width_r=None,
        )
        # Should not raise
        generated, errors = generate_unit(unit, profile, RoomContext())
        assert generated is not None
