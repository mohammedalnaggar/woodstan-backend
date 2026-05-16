"""Cabinet Domain Engine — public entry point.

The single public function is :func:`generate_unit`.  All other symbols are
implementation details; import from sub-modules only in tests.
"""

from __future__ import annotations

from engine.models.errors import ValidationError as _ValidationError
from engine.models.profile import WorkshopProfile as _WorkshopProfile
from engine.models.result import GeneratedUnit as _GeneratedUnit
from engine.models.room import RoomContext as _RoomContext
from engine.models.unit import UnitDefinition as _UnitDefinition

# Re-export for callers who prefer the flat import (no name pollution)
from engine.models.errors import ValidationError
from engine.models.result import GeneratedUnit

__all__ = ["generate_unit", "GeneratedUnit", "ValidationError"]


def generate_unit(
    unit: _UnitDefinition,
    profile: _WorkshopProfile,
    room: _RoomContext,
) -> tuple[_GeneratedUnit, list[_ValidationError]]:
    """Generate a complete cut list for a single cabinet unit.

    The engine is a pure function: no I/O, no database, no HTTP.
    All validation rules run regardless of earlier failures (collect-all).

    Args:
        unit:    Immutable cabinet specification.
        profile: Workshop-level settings (assembly method, thicknesses).
        room:    Ordered list of Unit IDs already assigned in the same room.

    Returns:
        A tuple of:
            - :class:`GeneratedUnit` with the assigned ID and all parts.
            - ``list[ValidationError]`` — empty if all rules passed,
              non-empty if one or more manufacturability rules were violated.
              The caller decides whether to surface or suppress these errors;
              a non-empty list does **not** prevent part generation.
    """
    from engine.generators.base import assign_unit_id, generate_parts
    from engine.resolvers.base import resolve_dimensions
    from engine.validators.runner import validate_unit

    unit_id = assign_unit_id(room)
    dims = resolve_dimensions(unit, profile)
    parts = generate_parts(unit_id, unit, dims, profile)
    parts_roles = frozenset(p.role.value for p in parts)
    errors = validate_unit(unit, dims, parts_roles)

    generated = _GeneratedUnit(
        unit_id=unit_id,
        unit_type=unit.unit_type,
        parts=parts,
    )
    return generated, errors
