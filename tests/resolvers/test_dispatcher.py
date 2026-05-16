"""Tests for the resolver dispatcher (base.resolve_dimensions)."""

import pytest

from engine.models.profile import AssemblyMethod, WorkshopProfile
from engine.models.unit import UnitDefinition, UnitType
from engine.resolvers.base import resolve_dimensions


@pytest.fixture
def unit():
    return UnitDefinition(
        unit_type=UnitType.lower,
        width=60.0,
        height=72.0,
        depth=58.0,
        shelf_count=0,
    )


def test_dispatches_full_sides(unit):
    profile = WorkshopProfile(
        assembly_method=AssemblyMethod.full_sides,
        carcass_thickness=1.855,
        back_panel_thickness=0.7,
        edge_banding_thickness=0.1,
    )
    dims = resolve_dimensions(unit, profile)
    # full_sides: side_height == unit.height
    assert dims.side_height == pytest.approx(72.0, rel=1e-6)
    assert dims.inner_width == pytest.approx(60.0 - 2 * 1.855, rel=1e-6)


def test_dispatches_full_top_bottom(unit):
    profile = WorkshopProfile(
        assembly_method=AssemblyMethod.full_top_bottom,
        carcass_thickness=1.855,
        back_panel_thickness=0.7,
        edge_banding_thickness=0.1,
    )
    dims = resolve_dimensions(unit, profile)
    # full_top_bottom: inner_width == unit.width
    assert dims.inner_width == pytest.approx(60.0, rel=1e-6)
    assert dims.side_height == pytest.approx(dims.inner_height, rel=1e-6)
