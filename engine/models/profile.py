"""Workshop Profile — global manufacturing settings shared across all projects."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

__all__ = ["AssemblyMethod", "WorkshopProfile"]


class AssemblyMethod(str, Enum):
    """Determines which panels are the outer (full-length) panels of the carcass.

    full_sides:
        Side panels run the full height H. Top and bottom panels sit between them.
        inner_width = W − 2 × carcass_thickness.

    full_top_bottom:
        Top and bottom panels run the full width W. Side panels sit between them.
        inner_height = H − 2 × carcass_thickness.
    """

    full_sides = "full_sides"
    full_top_bottom = "full_top_bottom"


@dataclass(frozen=True)
class WorkshopProfile:
    """Immutable global settings that govern all dimension calculations.

    Every engine call receives this profile explicitly — no hardcoded
    manufacturing constants are permitted anywhere in the engine.

    All thickness values are in centimetres (cm).
    """

    assembly_method: AssemblyMethod
    carcass_thickness: float        # e.g. 1.855 cm (18.55 mm)
    back_panel_thickness: float     # e.g. 0.7 cm  (7 mm)
    edge_banding_thickness: float   # e.g. 0.1 cm  (1 mm PVC)

    def __post_init__(self) -> None:
        if self.carcass_thickness <= 0:
            raise ValueError("carcass_thickness must be positive")
        if self.back_panel_thickness <= 0:
            raise ValueError("back_panel_thickness must be positive")
        if self.edge_banding_thickness < 0:
            raise ValueError("edge_banding_thickness must be non-negative")
