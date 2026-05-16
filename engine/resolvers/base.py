"""Resolver dispatcher — routes to the correct assembly-method implementation."""

from __future__ import annotations

from engine.models.profile import AssemblyMethod, WorkshopProfile
from engine.models.result import DimensionSet
from engine.models.unit import UnitDefinition
from engine.resolvers import full_sides, full_top_bottom


def resolve_dimensions(unit: UnitDefinition, profile: WorkshopProfile) -> DimensionSet:
    """Dispatch to the resolver matching ``profile.assembly_method``.

    Args:
        unit:    Cabinet specification.
        profile: Workshop settings (assembly_method determines which resolver runs).

    Returns:
        Populated :class:`DimensionSet` for the given assembly method.

    Raises:
        ValueError: If ``profile.assembly_method`` is not a known :class:`AssemblyMethod`.
    """
    if profile.assembly_method is AssemblyMethod.full_sides:
        return full_sides.resolve_dimensions(unit, profile)
    if profile.assembly_method is AssemblyMethod.full_top_bottom:
        return full_top_bottom.resolve_dimensions(unit, profile)
    raise ValueError(f"Unknown assembly method: {profile.assembly_method!r}")
