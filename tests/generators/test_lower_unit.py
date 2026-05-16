"""Tests for the lower unit structural part generator."""

import pytest

from engine.models.part import PartRole
from engine.models.profile import AssemblyMethod, WorkshopProfile
from engine.models.unit import UnitDefinition, UnitType
from engine.resolvers.base import resolve_dimensions
from engine.generators.lower import generate_structural


@pytest.fixture
def profile():
    return WorkshopProfile(
        assembly_method=AssemblyMethod.full_sides,
        carcass_thickness=1.855,
        back_panel_thickness=0.7,
        edge_banding_thickness=0.1,
    )


@pytest.fixture
def standard_lower():
    return UnitDefinition(
        unit_type=UnitType.lower,
        width=60.0, height=72.0, depth=58.0,
        shelf_count=0,
        is_corner=False,
    )


@pytest.fixture
def corner_lower():
    return UnitDefinition(
        unit_type=UnitType.lower,
        width=90.0, height=72.0, depth=58.0,
        shelf_count=0,
        is_corner=True,
    )


class TestLowerStructural:
    def test_non_corner_has_stf_and_stb(self, standard_lower, profile):
        dims = resolve_dimensions(standard_lower, profile)
        parts = generate_structural("CAB-001", standard_lower, dims, profile)
        roles = {p.role for p in parts}
        assert PartRole.STF in roles
        assert PartRole.STB in roles

    def test_non_corner_no_top_panel(self, standard_lower, profile):
        dims = resolve_dimensions(standard_lower, profile)
        parts = generate_structural("CAB-001", standard_lower, dims, profile)
        roles = {p.role for p in parts}
        assert PartRole.TP not in roles

    def test_corner_has_no_stretchers(self, corner_lower, profile):
        dims = resolve_dimensions(corner_lower, profile)
        parts = generate_structural("CAB-001", corner_lower, dims, profile)
        roles = {p.role for p in parts}
        assert PartRole.STF not in roles
        assert PartRole.STB not in roles

    def test_back_stretcher_has_groove(self, standard_lower, profile):
        dims = resolve_dimensions(standard_lower, profile)
        parts = generate_structural("CAB-001", standard_lower, dims, profile)
        stb = next(p for p in parts if p.role is PartRole.STB)
        assert stb.groove is True

    def test_front_stretcher_no_groove(self, standard_lower, profile):
        dims = resolve_dimensions(standard_lower, profile)
        parts = generate_structural("CAB-001", standard_lower, dims, profile)
        stf = next(p for p in parts if p.role is PartRole.STF)
        assert stf.groove is False

    def test_side_panels_use_carcass_thickness(self, standard_lower, profile):
        dims = resolve_dimensions(standard_lower, profile)
        parts = generate_structural("CAB-001", standard_lower, dims, profile)
        for p in parts:
            if p.role in (PartRole.LS, PartRole.RS):
                assert p.thickness == pytest.approx(profile.carcass_thickness)

    def test_back_panel_uses_back_panel_thickness(self, standard_lower, profile):
        dims = resolve_dimensions(standard_lower, profile)
        parts = generate_structural("CAB-001", standard_lower, dims, profile)
        bk = next(p for p in parts if p.role is PartRole.BK)
        assert bk.thickness == pytest.approx(profile.back_panel_thickness)

    def test_part_ids_contain_unit_id(self, standard_lower, profile):
        dims = resolve_dimensions(standard_lower, profile)
        parts = generate_structural("CAB-007", standard_lower, dims, profile)
        for p in parts:
            assert p.id.startswith("CAB-007-")
            assert p.unit_id == "CAB-007"

    def test_side_panel_length_equals_side_height(self, standard_lower, profile):
        dims = resolve_dimensions(standard_lower, profile)
        parts = generate_structural("CAB-001", standard_lower, dims, profile)
        ls = next(p for p in parts if p.role is PartRole.LS)
        # full_sides: side_height == unit.height
        assert ls.length == pytest.approx(72.0, rel=1e-6)

    def test_contains_ls_rs_bt_bk(self, standard_lower, profile):
        dims = resolve_dimensions(standard_lower, profile)
        parts = generate_structural("CAB-001", standard_lower, dims, profile)
        roles = {p.role for p in parts}
        assert {PartRole.LS, PartRole.RS, PartRole.BT, PartRole.BK}.issubset(roles)
