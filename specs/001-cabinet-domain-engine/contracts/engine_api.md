# Engine Public API Contract

**Branch**: `001-cabinet-domain-engine` | **Date**: 2026-05-16

This document defines the public interface contract for the Cabinet Domain Engine (Phase 1). The engine is a pure Python library — no HTTP, no database. These are the importable function signatures callers (tests in Phase 1, the FastAPI layer in Phase 3) must use.

---

## Primary Entry Point

```python
def generate_unit(
    profile: WorkshopProfile,
    unit: UnitDefinition,
    room_context: RoomContext,
) -> GeneratedUnit | list[ValidationError]:
    """
    Main engine entry point.

    Returns GeneratedUnit on success (all validation rules pass).
    Returns a non-empty list[ValidationError] if any rule is violated.
    Never returns both. Never raises on validation failure — only on
    programming errors (e.g., unsupported AssemblyMethod value).

    Pure function: no I/O, no side effects, no mutable state.
    Identical inputs always produce identical outputs.
    """
```

**Caller responsibilities**:
- Supply an accurate `room_context.existing_unit_ids` list — the engine trusts this value to assign the next Unit ID.
- Supply a valid `WorkshopProfile` — the engine validates unit definitions against it but does not validate the profile itself in Phase 1.

---

## Secondary Utilities (called internally; exposed for testing)

```python
def resolve_dimensions(
    profile: WorkshopProfile,
    unit: UnitDefinition,
) -> DimensionSet:
    """
    Compute all inner dimensions for the unit given the active assembly method.
    Pure function. Returns a DimensionSet (inner_width, inner_height,
    shelf_width, shelf_depth, back_panel_width, back_panel_height).
    """

def validate_unit(
    profile: WorkshopProfile,
    unit: UnitDefinition,
    dimensions: DimensionSet,
) -> list[ValidationError]:
    """
    Run all validation rules against the unit definition and its resolved
    dimensions. Returns an empty list if all rules pass.
    Collect-all: every rule is evaluated regardless of prior failures.
    Pure function.
    """

def generate_parts(
    profile: WorkshopProfile,
    unit: UnitDefinition,
    dimensions: DimensionSet,
    unit_id: str,
) -> list[Part]:
    """
    Generate the complete list of Part objects for a validated unit.
    Only called after validate_unit returns an empty list.
    Pure function. Parts are returned in a stable, deterministic order:
    structural panels first (sides, top/bottom/stretchers, back),
    then shelves, then drawers.
    """

def assign_unit_id(room_context: RoomContext) -> str:
    """
    Derive the next sequential Unit ID from the room context.
    E.g. 2 existing → "CAB-003".
    Pure function.
    """
```

---

## Module Layout (Python package)

```
engine/
├── __init__.py            # re-exports generate_unit; public surface
├── models/
│   ├── profile.py         # WorkshopProfile, AssemblyMethod
│   ├── unit.py            # UnitDefinition, UnitType, DrawerConfig, DrawerSlideType
│   ├── part.py            # Part, PartRole, EdgeBanding
│   ├── room.py            # RoomContext
│   ├── result.py          # GeneratedUnit, DimensionSet
│   └── errors.py          # ValidationError
├── resolvers/
│   ├── base.py            # resolve_dimensions dispatcher
│   ├── full_sides.py      # full_sides assembly method resolver
│   └── full_top_bottom.py # full_top_bottom assembly method resolver
├── generators/
│   ├── base.py            # generate_parts dispatcher + assign_unit_id
│   ├── lower.py           # lower unit part generation (sides, bottom, stretchers, back)
│   ├── upper.py           # mid/high-upper part generation (sides, top, bottom, back)
│   ├── shelves.py         # shelf generation (shared)
│   └── drawers.py         # drawer box part generation
└── validators/
    ├── runner.py           # validate_unit — collect-all runner
    └── rules.py            # one function per named validation rule
```

---

## Error Contract

All validation errors follow this exact shape. Tests MUST assert on field values, not on `message` string content.

```python
@dataclass(frozen=True)
class ValidationError:
    rule: str           # machine-readable e.g. "shelf_span_exceeded"
    offending_value: float  # in cm
    limit: float            # in cm
    message: str        # human-readable; not tested directly
```

Named rule strings (stable across versions — changing a rule name is a breaking change):

| Constant | Value |
|----------|-------|
| `RULE_SHELF_SPAN` | `"shelf_span_exceeded"` |
| `RULE_DRAWER_NOT_PERMITTED` | `"drawer_not_permitted"` |
| `RULE_DRAWER_WIDTH_CLEARANCE` | `"drawer_width_clearance"` |
| `RULE_PART_BELOW_MIN` | `"part_below_min_dimension"` |
| `RULE_PART_ABOVE_MAX` | `"part_above_max_dimension"` |
| `RULE_STRETCHER_MISSING` | `"stretcher_missing"` |
| `RULE_STRETCHER_ON_CORNER` | `"stretcher_on_corner"` |

---

## Usage Example (for tests and Phase 3 API)

```python
from engine import generate_unit
from engine.models.profile import WorkshopProfile, AssemblyMethod
from engine.models.unit import UnitDefinition, UnitType, DrawerConfig, DrawerSlideType
from engine.models.room import RoomContext

profile = WorkshopProfile(
    assembly_method=AssemblyMethod.full_sides,
    carcass_thickness=1.855,
    back_panel_thickness=0.7,
    edge_banding_thickness=0.1,
)

unit = UnitDefinition(
    unit_type=UnitType.lower,
    width=60.0,
    height=72.0,
    depth=56.0,
    shelf_count=1,
    drawers=[DrawerConfig(position=1, slide_type=DrawerSlideType.side_slides)],
    is_corner=False,
    face_width_L=None,  # only required for corner units in Phase 2+
    face_width_R=None,
)

room = RoomContext(existing_unit_ids=["CAB-001", "CAB-002"])

result = generate_unit(profile, unit, room)

if isinstance(result, list):
    # validation errors
    for err in result:
        print(err.rule, err.offending_value, err.limit)
else:
    # success
    print(result.unit_id)       # "CAB-003"
    for part in result.parts:
        print(part.id, part.length, part.width)
```
