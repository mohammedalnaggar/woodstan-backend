"""Generator utilities shared across all unit types.

assign_unit_id  — derives the next sequential Unit ID from the room context.
generate_parts  — dispatches to the correct unit-type generator and returns
                  the full ordered part list.
"""

from __future__ import annotations

import re

from engine.models.part import Part
from engine.models.profile import WorkshopProfile
from engine.models.result import DimensionSet, GeneratedUnit
from engine.models.room import RoomContext
from engine.models.unit import UnitDefinition, UnitType

# Unit ID format: CAB-NNN (zero-padded to 3 digits minimum)
_ID_PREFIX = "CAB"
_ID_RE = re.compile(r"^CAB-(\d+)$")


def assign_unit_id(room: RoomContext) -> str:
    """Derive the next sequential Unit ID for a new unit in *room*.

    Parses all existing ``CAB-NNN`` IDs, takes the maximum sequence number,
    and returns ``CAB-{max+1}`` zero-padded to at least three digits.

    Args:
        room: Current room state supplied by the caller.

    Returns:
        Next Unit ID string, e.g. ``"CAB-001"`` or ``"CAB-042"``.
    """
    max_seq = 0
    for uid in room.existing_unit_ids:
        m = _ID_RE.match(uid)
        if m:
            max_seq = max(max_seq, int(m.group(1)))
    next_seq = max_seq + 1
    return f"{_ID_PREFIX}-{next_seq:03d}"


def generate_parts(
    unit_id: str,
    unit: UnitDefinition,
    dims: DimensionSet,
    profile: WorkshopProfile,
) -> tuple[Part, ...]:
    """Dispatch to the appropriate generator and return the ordered part tuple.

    Part ordering: structural panels → shelves → drawers.

    Args:
        unit_id: Assigned unit identifier (e.g. ``"CAB-001"``).
        unit:    Cabinet specification.
        dims:    Pre-computed interior dimensions.
        profile: Workshop settings (material thicknesses).

    Returns:
        Immutable tuple of :class:`Part` objects.
    """
    from engine.generators import lower, upper, shelves, drawers

    parts: list[Part] = []

    if unit.unit_type is UnitType.lower:
        parts.extend(lower.generate_structural(unit_id, unit, dims, profile))
    else:
        parts.extend(upper.generate_structural(unit_id, unit, dims, profile))

    parts.extend(shelves.generate_shelves(unit_id, unit, dims, profile))
    parts.extend(drawers.generate_drawers(unit_id, unit, dims, profile))

    return tuple(parts)
