"""Collect-all validation runner.

Runs every rule against the unit + its computed dimensions and returns
the full list of violations rather than stopping at the first one.
An empty list means the unit passed all manufacturability checks.
"""

from __future__ import annotations

from typing import Sequence

from engine.models.errors import ValidationError
from engine.models.result import DimensionSet
from engine.models.unit import UnitDefinition
from engine.validators import rules


def validate_unit(
    unit: UnitDefinition,
    dims: DimensionSet,
    parts_roles: frozenset[str] | None = None,
) -> list[ValidationError]:
    """Run all validation rules and return every violation found.

    Args:
        unit:        The cabinet specification to validate.
        dims:        Pre-computed interior dimensions from the resolver.
        parts_roles: Set of :class:`PartRole` string values already generated
                     (used by stretcher-presence rules).  Pass ``None`` to
                     default to an empty frozenset — note this will trigger
                     ``stretcher_missing`` for lower non-corner units since STF
                     and STB will appear absent.

    Returns:
        List of :class:`ValidationError` objects — empty list means all clear.
    """
    if parts_roles is None:
        parts_roles = frozenset()

    errors: list[ValidationError] = []

    for check_result in [
        rules.check_shelf_span(unit, dims),
        rules.check_drawer_not_permitted(unit),
        rules.check_drawer_width_clearance(unit, dims),
        rules.check_part_below_min(dims),
        rules.check_part_above_max(dims),
        rules.check_stretcher_missing(unit, parts_roles),
        rules.check_stretcher_on_corner(unit, parts_roles),
    ]:
        if check_result is not None:
            errors.append(check_result)

    return errors
