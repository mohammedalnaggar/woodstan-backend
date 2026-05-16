"""Tests for the upper unit structural part generator (mid_upper / high_upper)."""

import pytest

from engine.models.part import PartRole
from engine.models.profile import AssemblyMethod, WorkshopProfile
from engine.models.unit import UnitDefinition, UnitType
from engine.resolvers.base import resolve_dimensions
from engine.generators.upper import generate_structural


@pytest.fixture
def profile():
    return WorkshopProfile(
        assembly_method=AssemblyMethod.full_sides,
        carcass_thickness=1.855,
        back_panel_thickness=0.7,
        edge_banding_thickness=0.1,
    )


@pytest.fixture
def mid_upper():
    return UnitDefinition(
        unit_type=UnitType.mid_upper,
        width=60.0, height=60.0, depth=35.0,
        shelf_count=0,
    )


@pytest.fixture
def high_upper():
    return UnitDefinition(
        unit_type=UnitType.high_upper,
        width=60.0, height=90.0, depth=35.0,
        shelf_count=0,
    )


class TestUpperStructural:
    def test_has_top_panel(self, mid_upper, profile):
        dims = resolve_dimensions(mid_upper, profile)
        parts = generate_structural("CAB-001", mid_upper, dims, profile)
        roles = {p.role for p in parts}
        assert PartRole.TP in roles

    def test_has_no_stretchers(self, mid_upper, profile):
        dims = resolve_dimensions(mid_upper, profile)
        parts = generate_structural("CAB-001", mid_upper, dims, profile)
        roles = {p.role for p in parts}
        assert PartRole.STF not in roles
        assert PartRole.STB not in roles

    def test_contains_all_structural_roles(self, mid_upper, profile):
        dims = resolve_dimensions(mid_upper, profile)
        parts = generate_structural("CAB-001", mid_upper, dims, profile)
        roles = {p.role for p in parts}
        assert {PartRole.LS, PartRole.RS, PartRole.TP, PartRole.BT, PartRole.BK}.issubset(roles)

    def test_upper_side_edge_banding(self, mid_upper, profile):
        """Upper unit side panels have top, front, and bottom banding."""
        dims = resolve_dimensions(mid_upper, profile)
        parts = generate_structural("CAB-001", mid_upper, dims, profile)
        ls = next(p for p in parts if p.role is PartRole.LS)
        assert ls.edge_banding.top is True
        assert ls.edge_banding.left is True
        assert ls.edge_banding.bottom is True

    def test_back_panel_thickness(self, high_upper, profile):
        dims = resolve_dimensions(high_upper, profile)
        parts = generate_structural("CAB-001", high_upper, dims, profile)
        bk = next(p for p in parts if p.role is PartRole.BK)
        assert bk.thickness == pytest.approx(profile.back_panel_thickness)

    def test_part_ids_prefixed_with_unit_id(self, mid_upper, profile):
        dims = resolve_dimensions(mid_upper, profile)
        parts = generate_structural("CAB-003", mid_upper, dims, profile)
        for p in parts:
            assert p.id.startswith("CAB-003-")

    def test_works_for_high_upper(self, high_upper, profile):
        dims = resolve_dimensions(high_upper, profile)
        parts = generate_structural("CAB-001", high_upper, dims, profile)
        assert len(parts) == 5  # LS, RS, TP, BT, BK

    def test_upper_corner_unit_no_stretchers(self, profile):
        """Corner upper units have the same carcass — no stretchers either way."""
        corner_upper = UnitDefinition(
            unit_type=UnitType.mid_upper,
            width=60.0, height=60.0, depth=35.0,
            shelf_count=0,
            is_corner=True,
        )
        dims = resolve_dimensions(corner_upper, profile)
        parts = generate_structural("CAB-001", corner_upper, dims, profile)
        roles = {p.role for p in parts}
        assert PartRole.STF not in roles
        assert PartRole.STB not in roles
