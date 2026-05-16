# Data Model: Cabinet Domain Engine

**Branch**: `001-cabinet-domain-engine` | **Date**: 2026-05-16

All values and field types below are implementation-language-agnostic. The Python implementation uses dataclasses with `frozen=True` for immutability.

---

## Enumerations

### `AssemblyMethod`
```
full_sides        — side panels cover top and bottom (sides are outer)
full_top_bottom   — top and bottom panels cover sides (top/bottom are outer)
```

### `UnitType`
```
lower       — base unit below countertop; may have drawers; uses stretchers
mid-upper   — upper unit at mid-height; doors only; no drawers
high-upper  — upper unit at high height; doors only; no drawers
```

### `DrawerSlideType`
```
side_slides    — rails on left and right of drawer body; 25mm total clearance
bottom_slides  — rail under drawer body; 6mm total clearance
```

### `PartRole`
```
LS   — left side panel
RS   — right side panel
TP   — top panel (upper units only)
BT   — bottom panel
STF  — front stretcher (lower units, non-corner only)
STB  — back stretcher (lower units, non-corner only)
SH   — shelf (sequenced)
BK   — back panel
DV   — divider (sequenced)
DD   — drawer door (sequenced by position from top)
DSL  — drawer depth panel left (perpendicular to door)
DSR  — drawer depth panel right
DWF  — drawer width panel front (parallel to door)
DWB  — drawer width panel back
```

---

## Core Models

### `WorkshopProfile`
Global settings entity. One per workshop. Passed explicitly to every engine call.

| Field | Type | Description |
|-------|------|-------------|
| `assembly_method` | `AssemblyMethod` | `full_sides` or `full_top_bottom` |
| `carcass_thickness` | float (cm) | Panel thickness for all structural carcass panels |
| `back_panel_thickness` | float (cm) | Thickness of the back panel (HDF/MDF) |
| `edge_banding_thickness` | float (cm) | PVC banding thickness applied to visible edges |

Default workshop values: `carcass_thickness=1.855`, `back_panel_thickness=0.7`, `edge_banding_thickness=0.1`

---

### `DrawerConfig`
Configuration for a single drawer within a lower unit.

| Field | Type | Description |
|-------|------|-------------|
| `position` | int (1-based) | Position from top; 1 = topmost drawer |
| `slide_type` | `DrawerSlideType` | Side or bottom slides |

---

### `UnitDefinition`
Immutable input to the engine alongside WorkshopProfile and RoomContext.

| Field | Type | Description |
|-------|------|-------------|
| `unit_type` | `UnitType` | `lower`, `mid-upper`, or `high-upper` |
| `width` | float (cm) | Outer width of the unit |
| `height` | float (cm) | Net carcass height (toe kick and countertop excluded) |
| `depth` | float (cm) | Outer depth of the unit |
| `shelf_count` | int ≥ 0 | Number of adjustable shelves |
| `drawers` | list[`DrawerConfig`] | Drawer configurations; must be empty for mid/high-upper |
| `is_corner` | bool | `True` for corner units of any type — two faces at 90°; disables stretchers on lower units |
| `face_width_L` | float \| None (cm) | Explicit left-face door width for corner units; required when `is_corner=True` (Phase 2); None in Phase 1 |
| `face_width_R` | float \| None (cm) | Explicit right-face door width for corner units; required when `is_corner=True` (Phase 2); None in Phase 1 |

**Constraints (validated before generation)**:
- `width`, `height`, `depth` > 0 (cm)
- `drawers` must be empty if `unit_type != lower`
- `is_corner` is valid for all unit types (`lower`, `mid-upper`, `high-upper`)
- For corner lower units: stretchers are not generated
- For corner upper units: carcass generation is identical to non-corner in Phase 1; door width handling (face_width_L/R) is enforced in Phase 2

---

### `RoomContext`
Caller-supplied context to determine the next sequential Unit ID.

| Field | Type | Description |
|-------|------|-------------|
| `existing_unit_ids` | list[str] | Ordered list of Unit IDs already in the room e.g. `["CAB-001", "CAB-002"]` |

**Unit ID assignment**: Next ID is derived from `len(existing_unit_ids) + 1`, zero-padded to 3 digits. E.g. 2 existing → next is `CAB-003`.

---

### `EdgeBanding`
Describes which edges of a panel are banded.

| Field | Type | Description |
|-------|------|-------------|
| `top` | bool | Top edge (width edge) |
| `left` | bool | Left edge (length edge — the front-facing edge for carcass panels) |
| `bottom` | bool | Bottom edge (width edge) |
| `right` | bool | Right edge (length edge) |

---

### `Part`
A single generated manufactured component. Immutable.

| Field | Type | Description |
|-------|------|-------------|
| `id` | str | Traceability identifier: `[UNIT_ID]-[PART_ROLE]-[SEQUENCE]` e.g. `CAB-001-LS-01` |
| `unit_id` | str | Parent unit identifier |
| `role` | `PartRole` | Semantic role within the unit |
| `length` | float (cm) | Longer dimension (grain direction) |
| `width` | float (cm) | Shorter dimension |
| `thickness` | float (cm) | Material thickness (from WorkshopProfile) |
| `quantity` | int | Number of identical parts (usually 1; paired panels may be 2) |
| `grain_direction` | str | `"vertical"` or `"horizontal"` |
| `edge_banding` | `EdgeBanding` | Which edges carry PVC banding |
| `groove` | bool | Whether this panel has a back-panel routed groove |
| `has_hinges` | bool | True for door panels |

---

### `GeneratedUnit`
The successful output of an engine call.

| Field | Type | Description |
|-------|------|-------------|
| `unit_id` | str | Assigned Unit ID (e.g. `CAB-003`) |
| `unit_type` | `UnitType` | As supplied |
| `parts` | list[`Part`] | Complete, ordered list of generated parts |

---

### `ValidationError`
Returned as part of a list when any validation rule is violated.

| Field | Type | Description |
|-------|------|-------------|
| `rule` | str | Machine-readable rule name e.g. `"shelf_span_exceeded"` |
| `offending_value` | float | The value that failed (in cm) |
| `limit` | float | The allowed threshold (in cm) |
| `message` | str | Human-readable description (for logging/UI display) |

---

## Validation Rules Reference

| Rule name | Trigger | `offending_value` | `limit` |
|-----------|---------|-------------------|---------|
| `shelf_span_exceeded` | `shelf_count > 0` and inner_width exceeds sag limit | inner_width (cm) | sag limit for thickness (cm) |
| `drawer_not_permitted` | drawers defined on mid/high-upper unit | len(drawers) | 0 |
| `drawer_width_clearance` | drawer width panel < minimum clearance | actual drawer width (cm) | minimum allowed (cm) |
| `part_below_min_dimension` | any generated part dimension < guard | offending dimension (cm) | minimum guard (cm) |
| `part_above_max_dimension` | any generated part dimension > guard | offending dimension (cm) | maximum guard (cm) |
| `stretcher_missing` | lower non-corner unit without stretchers | 0 (stretchers found) | 2 (required) |
| `stretcher_on_corner` | corner unit has stretchers | 2 (found) | 0 (required) |

---

## Relationships

```
WorkshopProfile ──────────────────────────────────────────────────────────┐
                                                                           │ read by all resolvers
RoomContext ──────────────────────────────────────────────────────────┐   │
                                                                       │   │
UnitDefinition ─────────────────────────────────────────────────┐     │   │
                                                                 │     │   │
                                                      Engine Call(profile, unit, room)
                                                                 │
                                            ┌────────────────────┤
                                            │                    │
                                    GeneratedUnit         list[ValidationError]
                                    (success path)        (failure path — never mixed)
                                            │
                                       list[Part]
                                    (immutable snapshot)
```

---

## Sag Limit Lookup Table

Used by `shelf_span_exceeded` validation rule. Keyed by `carcass_thickness` (cm).

| Thickness (cm) | Max span (cm) |
|----------------|---------------|
| 1.6 | 80 |
| 1.8 | 85 |
| 1.855 | 90 |
| default (unknown) | 85 |

---

## Part Generation Matrix

Which parts are generated per unit type:

| Part | lower (non-corner) | lower (corner) | mid-upper | high-upper |
|------|--------------------|----------------|-----------|------------|
| Side L + Side R | ✓ | ✓ | ✓ | ✓ |
| Top panel | ✗ | ✗ | ✓ | ✓ |
| Bottom panel | ✓ | ✓ | ✓ | ✓ |
| Front stretcher | ✓ | ✗ | ✗ | ✗ |
| Back stretcher | ✓ | ✗ | ✗ | ✗ |
| Back panel | ✓ | ✓ | ✓ | ✓ |
| Shelf(ves) | optional | optional | optional | optional |
| Drawer parts | optional | optional | ✗ | ✗ |
