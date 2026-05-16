"""Tests for the full_sides dimension resolver."""

import pytest

from engine.models.profile import AssemblyMethod, WorkshopProfile
from engine.models.unit import UnitDefinition, UnitType
from engine.resolvers.full_sides import resolve_dimensions


@pytest.fixture
def profile():
    return WorkshopProfile(
        assembly_method=AssemblyMethod.full_sides,
        carcass_thickness=1.855,
        back_panel_thickness=0.7,
        edge_banding_thickness=0.1,
    )


@pytest.fixture
def unit_60():
    return UnitDefinition(
        unit_type=UnitType.lower,
        width=60.0,
        height=72.0,
        depth=58.0,
        shelf_count=0,
    )


class TestFullSidesDimensions:
    def test_inner_width(self, unit_60, profile):
        dims = resolve_dimensions(unit_60, profile)
        assert dims.inner_width == pytest.approx(60.0 - 2 * 1.855, rel=1e-6)

    def test_inner_height(self, unit_60, profile):
        dims = resolve_dimensions(unit_60, profile)
        assert dims.inner_height == pytest.approx(72.0 - 2 * 1.855, rel=1e-6)

    def test_side_height_equals_external_height(self, unit_60, profile):
        """full_sides: sides cover top+bottom, so side_height == unit.height."""
        dims = resolve_dimensions(unit_60, profile)
        assert dims.side_height == pytest.approx(72.0, rel=1e-6)

    def test_shelf_width_has_clearance(self, unit_60, profile):
        dims = resolve_dimensions(unit_60, profile)
        assert dims.shelf_width == pytest.approx(dims.inner_width - 0.1, rel=1e-6)

    def test_shelf_depth_has_back_allowance(self, unit_60, profile):
        dims = resolve_dimensions(unit_60, profile)
        assert dims.shelf_depth == pytest.approx(58.0 - 3.0, rel=1e-6)

    def test_back_panel_width(self, unit_60, profile):
        dims = resolve_dimensions(unit_60, profile)
        # inner_width + 2 × groove_depth (0.8 cm each)
        assert dims.back_panel_width == pytest.approx(dims.inner_width + 1.6, rel=1e-6)

    def test_back_panel_height(self, unit_60, profile):
        dims = resolve_dimensions(unit_60, profile)
        assert dims.back_panel_height == pytest.approx(dims.inner_height + 1.6, rel=1e-6)

    def test_stretcher_width_equals_inner_width(self, unit_60, profile):
        dims = resolve_dimensions(unit_60, profile)
        assert dims.stretcher_width == pytest.approx(dims.inner_width, rel=1e-6)

    def test_stretcher_depth_fixed(self, unit_60, profile):
        dims = resolve_dimensions(unit_60, profile)
        assert dims.stretcher_depth == pytest.approx(10.0, rel=1e-6)

    def test_returns_dimension_set_type(self, unit_60, profile):
        from engine.models.result import DimensionSet
        dims = resolve_dimensions(unit_60, profile)
        assert isinstance(dims, DimensionSet)


class TestAssemblyMethodComparison:
    """T036 — same unit, both methods; verify expected dimension differences."""

    def test_full_sides_inner_width_narrower(self, unit_60):
        from engine.resolvers.full_top_bottom import resolve_dimensions as resolve_ftb
        t = 1.855
        profile_fs = WorkshopProfile(
            assembly_method=AssemblyMethod.full_sides,
            carcass_thickness=t,
            back_panel_thickness=0.7,
            edge_banding_thickness=0.1,
        )
        profile_ftb = WorkshopProfile(
            assembly_method=AssemblyMethod.full_top_bottom,
            carcass_thickness=t,
            back_panel_thickness=0.7,
            edge_banding_thickness=0.1,
        )
        dims_fs = resolve_dimensions(unit_60, profile_fs)
        dims_ftb = resolve_ftb(unit_60, profile_ftb)
        # full_sides deducts 2T from width; full_top_bottom does not
        assert dims_fs.inner_width == pytest.approx(dims_ftb.inner_width - 2 * t, rel=1e-6)

    def test_inner_height_identical_for_both_methods(self, unit_60):
        from engine.resolvers.full_top_bottom import resolve_dimensions as resolve_ftb
        t = 1.855
        profile_fs = WorkshopProfile(
            assembly_method=AssemblyMethod.full_sides,
            carcass_thickness=t,
            back_panel_thickness=0.7,
            edge_banding_thickness=0.1,
        )
        profile_ftb = WorkshopProfile(
            assembly_method=AssemblyMethod.full_top_bottom,
            carcass_thickness=t,
            back_panel_thickness=0.7,
            edge_banding_thickness=0.1,
        )
        dims_fs = resolve_dimensions(unit_60, profile_fs)
        dims_ftb = resolve_ftb(unit_60, profile_ftb)
        # Both methods deduct 2T from height
        assert dims_fs.inner_height == pytest.approx(dims_ftb.inner_height, rel=1e-6)
