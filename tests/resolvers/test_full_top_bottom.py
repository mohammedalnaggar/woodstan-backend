"""Tests for the full_top_bottom dimension resolver."""

import pytest

from engine.models.profile import AssemblyMethod, WorkshopProfile
from engine.models.unit import UnitDefinition, UnitType
from engine.resolvers.full_top_bottom import resolve_dimensions


@pytest.fixture
def profile():
    return WorkshopProfile(
        assembly_method=AssemblyMethod.full_top_bottom,
        carcass_thickness=1.855,
        back_panel_thickness=0.7,
        edge_banding_thickness=0.1,
    )


@pytest.fixture
def unit_80():
    return UnitDefinition(
        unit_type=UnitType.mid_upper,
        width=80.0,
        height=60.0,
        depth=35.0,
        shelf_count=0,
    )


class TestFullTopBottomDimensions:
    def test_inner_width_equals_external_width(self, unit_80, profile):
        """full_top_bottom: top/bottom span full width — inner_width == unit.width."""
        dims = resolve_dimensions(unit_80, profile)
        assert dims.inner_width == pytest.approx(80.0, rel=1e-6)

    def test_inner_height(self, unit_80, profile):
        dims = resolve_dimensions(unit_80, profile)
        assert dims.inner_height == pytest.approx(60.0 - 2 * 1.855, rel=1e-6)

    def test_side_height_equals_inner_height(self, unit_80, profile):
        """full_top_bottom: sides sit between top+bottom, so side_height == inner_height."""
        dims = resolve_dimensions(unit_80, profile)
        assert dims.side_height == pytest.approx(dims.inner_height, rel=1e-6)

    def test_shelf_width_has_clearance(self, unit_80, profile):
        dims = resolve_dimensions(unit_80, profile)
        assert dims.shelf_width == pytest.approx(dims.inner_width - 0.1, rel=1e-6)

    def test_shelf_depth_has_back_allowance(self, unit_80, profile):
        dims = resolve_dimensions(unit_80, profile)
        assert dims.shelf_depth == pytest.approx(35.0 - 3.0, rel=1e-6)

    def test_back_panel_width(self, unit_80, profile):
        dims = resolve_dimensions(unit_80, profile)
        assert dims.back_panel_width == pytest.approx(dims.inner_width + 1.6, rel=1e-6)

    def test_back_panel_height(self, unit_80, profile):
        dims = resolve_dimensions(unit_80, profile)
        assert dims.back_panel_height == pytest.approx(dims.inner_height + 1.6, rel=1e-6)

    def test_stretcher_dimensions(self, unit_80, profile):
        dims = resolve_dimensions(unit_80, profile)
        assert dims.stretcher_width == pytest.approx(dims.inner_width, rel=1e-6)
        assert dims.stretcher_depth == pytest.approx(10.0, rel=1e-6)
