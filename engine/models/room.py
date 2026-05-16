"""Room context — caller-supplied state for Unit ID assignment."""

from __future__ import annotations

from dataclasses import dataclass, field

__all__ = ["RoomContext"]


@dataclass(frozen=True)
class RoomContext:
    """Ordered list of Unit IDs already assigned in the same room.

    The engine uses this to assign the next sequential Unit ID without
    querying any external store.  In Phase 1 the caller (tests or the
    Phase 3 API layer) is responsible for supplying an accurate list.

    Example:
        existing_unit_ids=("CAB-001", "CAB-002")
        → next assigned ID will be "CAB-003"
    """

    existing_unit_ids: tuple[str, ...] = field(default_factory=tuple)
