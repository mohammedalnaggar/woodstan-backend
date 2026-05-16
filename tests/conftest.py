"""Shared pytest fixtures for the Cabinet Domain Engine test suite."""

import pytest

from engine.models.profile import AssemblyMethod, WorkshopProfile
from engine.models.room import RoomContext
from engine.models.unit import DrawerConfig, DrawerSlideType, UnitDefinition, UnitType


@pytest.fixture
def default_profile() -> WorkshopProfile:
    """Workshop profile using full_sides assembly (workshop standard)."""
    return WorkshopProfile(
        assembly_method=AssemblyMethod.full_sides,
        carcass_thickness=1.855,
        back_panel_thickness=0.7,
        edge_banding_thickness=0.1,
    )


@pytest.fixture
def full_top_bottom_profile() -> WorkshopProfile:
    """Workshop profile using full_top_bottom assembly."""
    return WorkshopProfile(
        assembly_method=AssemblyMethod.full_top_bottom,
        carcass_thickness=1.855,
        back_panel_thickness=0.7,
        edge_banding_thickness=0.1,
    )


@pytest.fixture
def empty_room() -> RoomContext:
    """Room with no existing units — next ID will be CAB-001."""
    return RoomContext(existing_unit_ids=())


@pytest.fixture
def room_with_two_units() -> RoomContext:
    """Room with two existing units — next ID will be CAB-003."""
    return RoomContext(existing_unit_ids=("CAB-001", "CAB-002"))


@pytest.fixture
def standard_lower_unit() -> UnitDefinition:
    """A typical lower unit: 60×72×56 cm, one shelf, no drawers."""
    return UnitDefinition(
        unit_type=UnitType.lower,
        width=60.0,
        height=72.0,
        depth=56.0,
        shelf_count=1,
        drawers=(),
        is_corner=False,
        face_width_l=None,
        face_width_r=None,
    )


@pytest.fixture
def standard_mid_upper() -> UnitDefinition:
    """A typical mid-upper unit: 60×45×35 cm, one shelf."""
    return UnitDefinition(
        unit_type=UnitType.mid_upper,
        width=60.0,
        height=45.0,
        depth=35.0,
        shelf_count=1,
        drawers=(),
        is_corner=False,
        face_width_l=None,
        face_width_r=None,
    )


@pytest.fixture
def lower_with_side_slide_drawer() -> UnitDefinition:
    """Lower unit with one side-slide drawer."""
    return UnitDefinition(
        unit_type=UnitType.lower,
        width=60.0,
        height=72.0,
        depth=56.0,
        shelf_count=0,
        drawers=(DrawerConfig(position=1, slide_type=DrawerSlideType.side_slides),),
        is_corner=False,
        face_width_l=None,
        face_width_r=None,
    )
