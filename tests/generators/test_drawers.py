"""Tests for the drawer box generator."""

import pytest

from engine.models.part import PartRole
from engine.models.profile import AssemblyMethod, WorkshopProfile
from engine.models.unit import DrawerConfig, DrawerSlideType, UnitDefinition, UnitType
from engine.resolvers.base import resolve_dimensions
from engine.generators.drawers import generate_drawers


@pytest.fixture
def profile():
    return WorkshopProfile(
        assembly_method=AssemblyMethod.full_sides,
        carcass_thickness=1.855,
        back_panel_thickness=0.7,
        edge_banding_thickness=0.1,
    )


def _lower_with_drawers(*drawers):
    return UnitDefinition(
        unit_type=UnitType.lower,
        width=60.0, height=72.0, depth=58.0,
        shelf_count=0,
        drawers=tuple(drawers),
    )


class TestDrawerGenerator:
    def test_no_drawers_returns_empty(self, profile):
        unit = _lower_with_drawers()
        dims = resolve_dimensions(unit, profile)
        assert generate_drawers("CAB-001", unit, dims, profile) == []

    def test_single_drawer_produces_five_parts(self, profile):
        drawer = DrawerConfig(position=1, slide_type=DrawerSlideType.side_slides)
        unit = _lower_with_drawers(drawer)
        dims = resolve_dimensions(unit, profile)
        parts = generate_drawers("CAB-001", unit, dims, profile)
        assert len(parts) == 5

    def test_drawer_roles_present(self, profile):
        drawer = DrawerConfig(position=1, slide_type=DrawerSlideType.side_slides)
        unit = _lower_with_drawers(drawer)
        dims = resolve_dimensions(unit, profile)
        parts = generate_drawers("CAB-001", unit, dims, profile)
        roles = {p.role for p in parts}
        assert roles == {PartRole.DD, PartRole.DSL, PartRole.DSR, PartRole.DWF, PartRole.DWB}

    def test_drawer_depth_panel_fixed_45cm(self, profile):
        drawer = DrawerConfig(position=1, slide_type=DrawerSlideType.side_slides)
        unit = _lower_with_drawers(drawer)
        dims = resolve_dimensions(unit, profile)
        parts = generate_drawers("CAB-001", unit, dims, profile)
        for p in parts:
            if p.role in (PartRole.DSL, PartRole.DSR):
                assert p.length == pytest.approx(45.0, rel=1e-6)

    def test_side_slide_clearance_applied(self, profile):
        """DWF/DWB width should be inner_width - 2.5 cm for side slides."""
        drawer = DrawerConfig(position=1, slide_type=DrawerSlideType.side_slides)
        unit = _lower_with_drawers(drawer)
        dims = resolve_dimensions(unit, profile)
        parts = generate_drawers("CAB-001", unit, dims, profile)
        for p in parts:
            if p.role in (PartRole.DWF, PartRole.DWB):
                assert p.length == pytest.approx(dims.inner_width - 2.5, rel=1e-6)

    def test_bottom_slide_clearance_applied(self, profile):
        """DWF/DWB width should be inner_width - 0.6 cm for bottom slides."""
        drawer = DrawerConfig(position=1, slide_type=DrawerSlideType.bottom_slides)
        unit = _lower_with_drawers(drawer)
        dims = resolve_dimensions(unit, profile)
        parts = generate_drawers("CAB-001", unit, dims, profile)
        for p in parts:
            if p.role in (PartRole.DWF, PartRole.DWB):
                assert p.length == pytest.approx(dims.inner_width - 0.6, rel=1e-6)

    def test_two_drawers_ten_parts(self, profile):
        d1 = DrawerConfig(position=1, slide_type=DrawerSlideType.side_slides)
        d2 = DrawerConfig(position=2, slide_type=DrawerSlideType.side_slides)
        unit = _lower_with_drawers(d1, d2)
        dims = resolve_dimensions(unit, profile)
        parts = generate_drawers("CAB-001", unit, dims, profile)
        assert len(parts) == 10

    def test_drawer_door_has_all_four_edge_banding(self, profile):
        drawer = DrawerConfig(position=1, slide_type=DrawerSlideType.side_slides)
        unit = _lower_with_drawers(drawer)
        dims = resolve_dimensions(unit, profile)
        parts = generate_drawers("CAB-001", unit, dims, profile)
        dd = next(p for p in parts if p.role is PartRole.DD)
        eb = dd.edge_banding
        assert eb.top and eb.left and eb.bottom and eb.right

    def test_drawer_ids_contain_sequence(self, profile):
        d1 = DrawerConfig(position=1, slide_type=DrawerSlideType.side_slides)
        d2 = DrawerConfig(position=2, slide_type=DrawerSlideType.side_slides)
        unit = _lower_with_drawers(d1, d2)
        dims = resolve_dimensions(unit, profile)
        parts = generate_drawers("CAB-001", unit, dims, profile)
        ids = [p.id for p in parts]
        assert any("01" in pid for pid in ids)
        assert any("02" in pid for pid in ids)
