"""Tests for the collect-all validation runner."""

import pytest

from engine.models.errors import (
    RULE_PART_BELOW_MIN,
    RULE_SHELF_SPAN,
)
from engine.models.profile import AssemblyMethod, WorkshopProfile
from engine.models.result import DimensionSet
from engine.models.unit import UnitDefinition, UnitType
from engine.validators.runner import validate_unit


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


def _lower(width=60.0, height=72.0, depth=58.0, shelf_count=0):
    return UnitDefinition(
        unit_type=UnitType.lower,
        width=width, height=height, depth=depth,
        shelf_count=shelf_count,
    )


class TestCollectAllRunner:
    def test_clean_unit_returns_empty_list(self, profile):
        unit = _lower()
        dims = _make_dims()
        roles = frozenset({"LS", "RS", "BT", "STF", "STB", "BK"})
        errors = validate_unit(unit, dims, roles)
        assert errors == []

    def test_collects_multiple_errors(self, profile):
        """Both shelf_span and part_below_min should surface in one pass."""
        unit = _lower()
        # shelf_width > 90 triggers RULE_SHELF_SPAN
        # inner_width < 5 triggers RULE_PART_BELOW_MIN
        dims = _make_dims(shelf_width=91.0, inner_width=4.0)
        errors = validate_unit(unit, dims)
        rules_fired = {e.rule for e in errors}
        assert RULE_SHELF_SPAN in rules_fired
        assert RULE_PART_BELOW_MIN in rules_fired

    def test_returns_list_of_validation_errors(self, profile):
        from engine.models.errors import ValidationError
        unit = _lower()
        dims = _make_dims(shelf_width=91.0)
        errors = validate_unit(unit, dims)
        assert all(isinstance(e, ValidationError) for e in errors)

    def test_none_parts_roles_triggers_stretcher_missing(self, profile):
        """Passing parts_roles=None (→ empty frozenset) triggers stretcher_missing
        for a lower non-corner unit because STF/STB appear absent."""
        from engine.models.errors import RULE_STRETCHER_MISSING
        unit = _lower()
        dims = _make_dims()
        errors = validate_unit(unit, dims, parts_roles=None)
        rules_fired = {e.rule for e in errors}
        assert RULE_STRETCHER_MISSING in rules_fired

    def test_corner_lower_with_no_roles_does_not_trigger_stretcher_missing(self):
        """Corner lower units skip the stretcher presence check entirely."""
        corner = UnitDefinition(
            unit_type=UnitType.lower,
            width=90.0, height=72.0, depth=58.0,
            shelf_count=0,
            is_corner=True,
        )
        dims = _make_dims()
        errors = validate_unit(corner, dims, parts_roles=None)
        from engine.models.errors import RULE_STRETCHER_MISSING
        assert not any(e.rule == RULE_STRETCHER_MISSING for e in errors)
