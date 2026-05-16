"""Part model — a single manufactured panel with full traceability metadata."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

__all__ = ["PartRole", "EdgeBanding", "Part"]


class PartRole(str, Enum):
    """Semantic role of a generated part within its unit.

    Each abbreviation maps to the [PART_ROLE] segment of the
    traceability identifier: [UNIT_ID]-[PART_ROLE]-[SEQUENCE].
    """

    # Structural carcass panels
    LS = "LS"    # left side panel
    RS = "RS"    # right side panel
    TP = "TP"    # top panel (upper units only)
    BT = "BT"    # bottom panel
    STF = "STF"  # front stretcher (lower non-corner units only)
    STB = "STB"  # back stretcher (lower non-corner units only; has groove)
    BK = "BK"    # back panel

    # Interior fittings
    SH = "SH"    # shelf (sequenced)
    DV = "DV"    # vertical divider (sequenced)

    # Drawer components
    DD = "DD"    # drawer door / external front (sequenced by position)
    DSL = "DSL"  # drawer depth panel — left (perpendicular to door)
    DSR = "DSR"  # drawer depth panel — right
    DWF = "DWF"  # drawer width panel — front (parallel to door)
    DWB = "DWB"  # drawer width panel — back


@dataclass(frozen=True)
class EdgeBanding:
    """Which edges of a panel carry PVC edge banding.

    Orientation reference (panel laid flat, door/front face toward viewer):
        top    — top edge (width direction)
        left   — left edge (length direction; typically the front-facing edge)
        bottom — bottom edge (width direction)
        right  — right edge (length direction; typically the back edge)
    """

    top: bool = False
    left: bool = False
    bottom: bool = False
    right: bool = False

    # Convenience constructors
    @classmethod
    def front_only(cls) -> EdgeBanding:
        return cls(left=True)

    @classmethod
    def all_four(cls) -> EdgeBanding:
        return cls(top=True, left=True, bottom=True, right=True)

    @classmethod
    def upper_side(cls) -> EdgeBanding:
        """Upper unit side panel: front + top + bottom."""
        return cls(top=True, left=True, bottom=True)

    @classmethod
    def none(cls) -> EdgeBanding:
        return cls()


@dataclass(frozen=True)
class Part:
    """A single manufactured component — immutable once generated.

    All dimension values (length, width, thickness) are in centimetres (cm).

    The traceability identifier follows the schema:
        [UNIT_ID]-[PART_ROLE]-[SEQUENCE]
    e.g. CAB-001-LS-01 = Cabinet 001, Left Side, Part 01.

    length:
        The longer of the two cutting dimensions.
        For carcass panels: the dimension parallel to the grain.
        For doors: always the vertical (height) dimension.

    width:
        The shorter of the two cutting dimensions.
    """

    id: str                     # e.g. "CAB-001-LS-01"
    unit_id: str                # e.g. "CAB-001"
    role: PartRole
    length: float               # cm — longer cut dimension
    width: float                # cm — shorter cut dimension
    thickness: float            # cm — material thickness
    quantity: int               # always 1 in Phase 1
    grain_direction: str        # "vertical" or "horizontal"
    edge_banding: EdgeBanding
    groove: bool                # back-panel routed groove present
    has_hinges: bool            # True for door panels (Phase 2+)
