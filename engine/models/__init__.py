"""Public model types for the Cabinet Domain Engine.

Single import surface — callers import from ``engine.models`` rather than
reaching into individual sub-modules.
"""

from engine.models.errors import (
    ValidationError,
    RULE_SHELF_SPAN,
    RULE_DRAWER_NOT_PERMITTED,
    RULE_DRAWER_WIDTH_CLEARANCE,
    RULE_PART_BELOW_MIN,
    RULE_PART_ABOVE_MAX,
    RULE_STRETCHER_MISSING,
    RULE_STRETCHER_ON_CORNER,
)
from engine.models.part import EdgeBanding, Part, PartRole
from engine.models.profile import AssemblyMethod, WorkshopProfile
from engine.models.result import DimensionSet, GeneratedUnit
from engine.models.room import RoomContext
from engine.models.unit import DrawerConfig, DrawerSlideType, UnitDefinition, UnitType

__all__ = [
    # errors
    "ValidationError",
    "RULE_SHELF_SPAN",
    "RULE_DRAWER_NOT_PERMITTED",
    "RULE_DRAWER_WIDTH_CLEARANCE",
    "RULE_PART_BELOW_MIN",
    "RULE_PART_ABOVE_MAX",
    "RULE_STRETCHER_MISSING",
    "RULE_STRETCHER_ON_CORNER",
    # parts
    "EdgeBanding",
    "Part",
    "PartRole",
    # profile
    "AssemblyMethod",
    "WorkshopProfile",
    # result
    "DimensionSet",
    "GeneratedUnit",
    # room
    "RoomContext",
    # unit
    "DrawerConfig",
    "DrawerSlideType",
    "UnitDefinition",
    "UnitType",
]
