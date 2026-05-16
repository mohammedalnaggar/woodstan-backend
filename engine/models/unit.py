"""Unit definition — the immutable input describing a single cabinet."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

__all__ = [
    "UnitType",
    "DrawerSlideType",
    "DrawerConfig",
    "UnitDefinition",
]


class UnitType(str, Enum):
    """The three permitted cabinet unit categories.

    lower:
        Base unit below the countertop. May have drawers.
        Uses front and back stretchers in place of a top panel
        (except corner units).

    mid_upper:
        Upper unit at mid-height (over countertop, reachable).
        Doors only — no drawers permitted.

    high_upper:
        Upper unit at high height (above mid-uppers).
        Doors only — no drawers permitted.
    """

    lower = "lower"
    mid_upper = "mid-upper"
    high_upper = "high-upper"


class DrawerSlideType(str, Enum):
    """Hardware mounting type for drawer slides.

    side_slides:
        Rails mounted on left and right of the drawer body.
        Total clearance deducted: 2.5 cm (25 mm).

    bottom_slides:
        Rail mounted under the drawer body.
        Total clearance deducted: 0.6 cm (6 mm).
    """

    side_slides = "side_slides"
    bottom_slides = "bottom_slides"


@dataclass(frozen=True)
class DrawerConfig:
    """Configuration for a single drawer within a lower unit."""

    position: int           # 1-based; 1 = topmost drawer
    slide_type: DrawerSlideType

    def __post_init__(self) -> None:
        if self.position < 1:
            raise ValueError("Drawer position must be >= 1")


@dataclass(frozen=True)
class UnitDefinition:
    """Immutable specification of a single cabinet unit.

    All dimensions (width, height, depth) are in centimetres (cm).
    The height is the net carcass height — toe kick and countertop
    allowances are NOT included here.

    is_corner applies to all unit types:
    - lower + is_corner=True  → no stretchers generated
    - upper + is_corner=True  → carcass unchanged in Phase 1;
                                 face_width_l/r required in Phase 2
                                 for correct door width calculation
    """

    unit_type: UnitType
    width: float            # outer width (cm)
    height: float           # net carcass height (cm)
    depth: float            # outer depth (cm)
    shelf_count: int        # number of adjustable shelves (0 = open)
    drawers: tuple[DrawerConfig, ...] = field(default_factory=tuple)
    is_corner: bool = False
    face_width_l: Optional[float] = None   # corner left-face door width (cm); Phase 2+
    face_width_r: Optional[float] = None   # corner right-face door width (cm); Phase 2+

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0 or self.depth <= 0:
            raise ValueError("Unit dimensions must be positive (cm)")
        if self.shelf_count < 0:
            raise ValueError("shelf_count must be >= 0")
        if self.drawers and self.unit_type != UnitType.lower:
            raise ValueError(
                f"Drawers are only valid for lower units, not {self.unit_type.value}"
            )
