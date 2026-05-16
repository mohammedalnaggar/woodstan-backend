"""Tests for individual validation rules.

All assertions use the RULE_* constants — never the message field.
"""

import pytest

from engine.models.errors import (
    RULE_DRAWER_NOT_PERMITTED,
    RULE_DRAWER_WIDTH_CLEARANCE,
    RULE_PART_ABOVE_MAX,
    RULE_PART_BELOW_MIN,
    RULE_SHELF_SPAN,
    RULE_STRETCHER_MISSING,
    RULE_STRETCHER_ON_CORNER,
)
from engine.models.profile import AssemblyMethod, WorkshopProfile
from engine.models.result import DimensionSet
from engine.models.unit import DrawerConfig, DrawerSlideType, UnitDefinition, UnitType
from engine.validators import rules as r


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def profile():
    return WorkshopProfile(
        assembly_method=AssemblyMethod.full_sides,
        carcass_thickness=1.855,
        back_panel_thickness=0.7,
        edge_banding_thickness=0.1,
    )


def _make_dims(**overrides) -> DimensionSet:
    defaults = dict(
        inner_width=56.29,
        inner_height=68.29,
        side_height=72.0,
        shelf_width=56.19,
        shelf_depth=55.0,
        back_panel_width=57.89,
        back_panel_height=69.89,
        stretcher_width=56.29,
        stretcher_depth=10.0,
    )
    defaults.update(overrides)
    return DimensionSet(**defaults)


def _lower(width=60.0, height=72.0, depth=58.0, shelf_count=0,
           is_corner=False, drawers=()):
    return UnitDefinition(
        unit_type=UnitType.lower,
        width=width, height=height, depth=depth,
        shelf_count=shelf_count,
        drawers=tuple(drawers),
        is_corner=is_corner,
    )


# ---------------------------------------------------------------------------
# check_shelf_span
# ---------------------------------------------------------------------------

class TestShelfSpan:
    def test_pass_within_limit(self):
        dims = _make_dims(shelf_width=89.9)
        assert r.check_shelf_span(_lower(), dims) is None

    def test_pass_at_limit(self):
        dims = _make_dims(shelf_width=90.0)
        assert r.check_shelf_span(_lower(), dims) is None

    def test_fail_exceeds_limit(self):
        dims = _make_dims(shelf_width=90.1)
        err = r.check_shelf_span(_lower(), dims)
        assert err is not None
        assert err.rule == RULE_SHELF_SPAN
        assert err.offending_value > 90.0
        assert err.limit == 90.0


# ---------------------------------------------------------------------------
# check_drawer_not_permitted
# ---------------------------------------------------------------------------

class TestDrawerNotPermitted:
    def test_pass_lower_with_drawer(self):
        drawer = DrawerConfig(position=1, slide_type=DrawerSlideType.side_slides)
        unit = _lower(drawers=[drawer])
        assert r.check_drawer_not_permitted(unit) is None

    def test_pass_upper_no_drawer(self):
        unit = UnitDefinition(
            unit_type=UnitType.mid_upper,
            width=60.0, height=60.0, depth=35.0,
            shelf_count=0,
        )
        assert r.check_drawer_not_permitted(unit) is None

    def test_fail_upper_with_drawer_raises_before_check(self):
        """UnitDefinition.__post_init__ rejects drawers on non-lower; validated there."""
        with pytest.raises(ValueError):
            UnitDefinition(
                unit_type=UnitType.mid_upper,
                width=60.0, height=60.0, depth=35.0,
                shelf_count=0,
                drawers=(DrawerConfig(position=1, slide_type=DrawerSlideType.side_slides),),
            )


# ---------------------------------------------------------------------------
# check_drawer_width_clearance
# ---------------------------------------------------------------------------

class TestDrawerWidthClearance:
    def test_pass_ample_width_side_slides(self):
        drawer = DrawerConfig(position=1, slide_type=DrawerSlideType.side_slides)
        unit = _lower(drawers=[drawer])
        dims = _make_dims(inner_width=40.0)  # 40 - 2.5 = 37.5 > 5
        assert r.check_drawer_width_clearance(unit, dims) is None

    def test_fail_too_narrow_side_slides(self):
        drawer = DrawerConfig(position=1, slide_type=DrawerSlideType.side_slides)
        unit = _lower(drawers=[drawer])
        # inner_width = 7.0 → body = 7.0 - 2.5 = 4.5 < 5.0
        dims = _make_dims(inner_width=7.0)
        err = r.check_drawer_width_clearance(unit, dims)
        assert err is not None
        assert err.rule == RULE_DRAWER_WIDTH_CLEARANCE

    def test_pass_bottom_slides_more_clearance(self):
        drawer = DrawerConfig(position=1, slide_type=DrawerSlideType.bottom_slides)
        unit = _lower(drawers=[drawer])
        dims = _make_dims(inner_width=6.0)  # 6.0 - 0.6 = 5.4 > 5
        assert r.check_drawer_width_clearance(unit, dims) is None

    def test_no_drawers_always_passes(self):
        unit = _lower()
        dims = _make_dims(inner_width=5.0)
        assert r.check_drawer_width_clearance(unit, dims) is None


# ---------------------------------------------------------------------------
# check_part_below_min
# ---------------------------------------------------------------------------

class TestPartBelowMin:
    def test_pass_all_above_min(self):
        dims = _make_dims()
        assert r.check_part_below_min(dims) is None

    def test_fail_inner_width_too_small(self):
        dims = _make_dims(inner_width=4.9)
        err = r.check_part_below_min(dims)
        assert err is not None
        assert err.rule == RULE_PART_BELOW_MIN
        assert err.offending_value < 5.0

    def test_fail_shelf_depth_too_small(self):
        dims = _make_dims(shelf_depth=4.0)
        err = r.check_part_below_min(dims)
        assert err is not None
        assert err.rule == RULE_PART_BELOW_MIN


# ---------------------------------------------------------------------------
# check_part_above_max
# ---------------------------------------------------------------------------

class TestPartAboveMax:
    def test_pass_all_below_max(self):
        dims = _make_dims()
        assert r.check_part_above_max(dims) is None

    def test_fail_inner_width_too_large(self):
        dims = _make_dims(inner_width=300.1)
        err = r.check_part_above_max(dims)
        assert err is not None
        assert err.rule == RULE_PART_ABOVE_MAX
        assert err.offending_value > 300.0


# ---------------------------------------------------------------------------
# check_stretcher_missing
# ---------------------------------------------------------------------------

class TestStretcherMissing:
    def test_pass_non_corner_with_stretchers(self):
        unit = _lower(is_corner=False)
        roles = frozenset({"STF", "STB"})
        assert r.check_stretcher_missing(unit, roles) is None

    def test_fail_non_corner_missing_stf(self):
        unit = _lower(is_corner=False)
        roles = frozenset({"STB"})
        err = r.check_stretcher_missing(unit, roles)
        assert err is not None
        assert err.rule == RULE_STRETCHER_MISSING

    def test_fail_non_corner_missing_both(self):
        unit = _lower(is_corner=False)
        roles = frozenset({"LS", "RS", "BT", "BK"})
        err = r.check_stretcher_missing(unit, roles)
        assert err is not None
        assert err.rule == RULE_STRETCHER_MISSING

    def test_pass_corner_skips_rule(self):
        unit = _lower(is_corner=True)
        roles = frozenset()
        assert r.check_stretcher_missing(unit, roles) is None

    def test_pass_upper_unit_skips_rule(self):
        unit = UnitDefinition(
            unit_type=UnitType.mid_upper,
            width=60.0, height=60.0, depth=35.0,
            shelf_count=0,
        )
        roles = frozenset()
        assert r.check_stretcher_missing(unit, roles) is None


# ---------------------------------------------------------------------------
# check_stretcher_on_corner
# ---------------------------------------------------------------------------

class TestStretcherOnCorner:
    def test_pass_corner_no_stretchers(self):
        unit = _lower(is_corner=True)
        roles = frozenset({"LS", "RS", "BT", "BK"})
        assert r.check_stretcher_on_corner(unit, roles) is None

    def test_fail_corner_has_stretcher(self):
        unit = _lower(is_corner=True)
        roles = frozenset({"LS", "RS", "BT", "STF", "STB", "BK"})
        err = r.check_stretcher_on_corner(unit, roles)
        assert err is not None
        assert err.rule == RULE_STRETCHER_ON_CORNER

    def test_pass_non_corner_with_stretchers(self):
        unit = _lower(is_corner=False)
        roles = frozenset({"STF", "STB"})
        assert r.check_stretcher_on_corner(unit, roles) is None

    def test_pass_upper_unit_skips_rule(self):
        unit = UnitDefinition(
            unit_type=UnitType.high_upper,
            width=60.0, height=60.0, depth=35.0,
            shelf_count=0,
        )
        roles = frozenset({"STF"})  # impossible in practice but rule should skip
        assert r.check_stretcher_on_corner(unit, roles) is None
