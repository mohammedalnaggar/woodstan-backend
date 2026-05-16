# Research: Cabinet Domain Engine

**Branch**: `001-cabinet-domain-engine` | **Date**: 2026-05-16

---

## 1. Shelf Sag Limits by Material Thickness

**Decision**: Use thickness-based maximum unsupported shelf spans derived from standard workshop practice.

| Carcass thickness (cm) | Material assumed | Max span (cm) |
|------------------------|-----------------|---------------|
| 1.6cm (16mm)           | MDF             | 80cm          |
| 1.855cm (18.55mm)      | MDF / board     | 90cm          |
| 1.8cm (18mm)           | MDF             | 85cm          |
| 1.8cm (18mm plywood)   | Plywood         | 120cm         |

**Rationale**: Industry-standard rule of thumb for kitchen cabinetry. Spans beyond these produce visible sag under typical shelf loads (crockery, books). The engine uses the Workshop Profile's `carcass_thickness` to look up the applicable limit. Material type is not in scope for Phase 1 — thickness is the proxy.

**Implementation note**: The sag table is a small lookup dict inside the validator. If the profile thickness does not appear in the table, the engine uses 85cm as a safe default. This avoids silent acceptance of unknown thicknesses.

**Alternatives considered**: Per-material-type rules — rejected because the Workshop Profile (Phase 1) does not carry material type; that is introduced in Phase 6.

---

## 2. Dimension Guards (Minimum and Maximum)

**Decision**: The following guards are enforced per part type. All values in cm.

| Part type | Min width (cm) | Min height / length (cm) | Max width (cm) | Notes |
|-----------|---------------|--------------------------|----------------|-------|
| Side panel | 5.0 | 20.0 | N/A | Height = unit H; width = unit D − back allowance |
| Top / Bottom panel | 5.0 | 5.0 | N/A | |
| Stretcher | 5.0 | 10.0 (fixed depth) | N/A | Depth is always 10cm; width = inner_width |
| Shelf | 5.0 | 5.0 | 120.0 | Max governed by sag table |
| Back panel | 5.0 | 20.0 | N/A | |
| Drawer depth panel | 5.0 | 45.0 (fixed length) | N/A | Length always 45cm (workshop standard) |
| Drawer width panel | 5.0 | 5.0 | N/A | |

**Rationale**: Panels below 5cm are not practically manufacturable on standard panel saws or CNC tables. 20cm minimum height prevents degenerate cabinet definitions. Drawer depth panel is fixed at 45cm (converted from the workshop's 450mm standard for drawer slide hardware).

**Alternatives considered**: No guards at all — rejected because the spec requires `Minimum and maximum dimension guards must be enforced per part type` (FR-009).

---

## 3. Part Label Role Abbreviations

**Decision**: The following abbreviation table maps part roles to the `[PART_ROLE]` segment of the traceability identifier `[UNIT_ID]-[PART_ROLE]-[SEQUENCE]`.

| Part role | Abbreviation | Notes |
|-----------|-------------|-------|
| Left side panel | `LS` | |
| Right side panel | `RS` | |
| Top panel | `TP` | Upper units only |
| Bottom panel | `BT` | All unit types |
| Front stretcher | `STF` | Lower units only |
| Back stretcher | `STB` | Lower units only |
| Shelf | `SH` | Sequenced: SH-01, SH-02 … |
| Back panel | `BK` | |
| Divider | `DV` | Sequenced: DV-01, DV-02 … |
| Drawer door | `DD` | Sequenced per drawer position |
| Drawer depth panel (left) | `DSL` | Perpendicular to door, left side |
| Drawer depth panel (right) | `DSR` | Perpendicular to door, right side |
| Drawer width panel (front) | `DWF` | Parallel to door, front |
| Drawer width panel (back) | `DWB` | Parallel to door, back |

**Rationale**: Abbreviated codes must be short enough to fit on physical part labels, unambiguous within a unit, and consistent with the SKILL.md naming convention (`U{n}_Side_L`, `U{n}_Stretch_Back`, etc.). The abbreviations map directly from the Blender naming tokens.

**Alternatives considered**: Full English names in labels — rejected because labels are printed on small physical stickers and must be readable at a glance on the shop floor.

---

## 4. Dimension Formulas per Assembly Method

**Decision**: Exact formulas derived from `skills/cabinet-specs/SKILL.md` and confirmed against constitution Principle IV. All values in cm. `T` = `carcass_thickness` from Workshop Profile.

### `full_sides` assembly (sides are outer panels)

```
inner_width        = W − (2 × T)
inner_height       = H − (2 × T)
shelf_width        = W − (2 × T) − 0.1        # 1mm clearance each side
shelf_depth        = D − 3.0                   # 30mm back allowance (in cm)
back_panel_width   = inner_width + (2 × back_T)
back_panel_height  = inner_height + (2 × back_T)

# Lower unit top replacement:
stretcher_depth    = 10.0   # fixed 100mm in cm
stretcher_width    = inner_width

# Side panels:
side_panel_height  = H      # sides run full height
side_panel_depth   = D − 3.0 − back_T   # depth minus back groove allowance
```

### `full_top_bottom` assembly (top/bottom are outer panels)

```
inner_width        = W          # top and bottom are full width
inner_height       = H − (2 × T)
shelf_width        = W − 0.1    # 1mm clearance
shelf_depth        = D − 3.0

back_panel_width   = inner_width + (2 × back_T)
back_panel_height  = inner_height + (2 × back_T)

# Side panels:
side_panel_height  = inner_height   # sides sit between top and bottom
side_panel_depth   = D − 3.0 − back_T
```

**Rationale**: Directly from SKILL.md construction section and constitution Principle IV. No research was required — these are established workshop standards.

---

## 5. Drawer Dimension Formulas

**Decision**: Derived directly from `skills/cabinet-specs/SKILL.md`. All values in cm.

```
drawer_body_height      = door_height − 2.0        # 20mm deduction
drawer_depth_panel_len  = 45.0                      # always 45cm (fixed hardware standard)
drawer_width_side_slide = W − (4 × T) − 2.5        # 25mm slide clearance total
drawer_width_bot_slide  = W − (4 × T) − 0.6        # 6mm slide clearance total
```

**Alternatives considered**: Making drawer depth configurable — rejected because 450mm is a fixed hardware constraint for the drawer slide runners used in this workshop.

---

## 6. Corner Unit Exception

**Decision**: A corner unit is identified by a boolean flag `is_corner` on the unit definition. When `is_corner=True` and unit type is `lower`, the engine MUST NOT generate stretchers and MUST NOT enforce the stretcher validation rule.

**Rationale**: Corner units have non-standard internal structures (carousel or fixed shelf arrangements) that preclude standard stretchers. This is an explicit exception to the lower-unit stretcher rule (Constitution Principle IV, v1.1.0).

**Alternatives considered**: A separate `corner_lower` unit type — rejected as over-engineering. The boolean flag on an existing `lower` type is simpler and keeps the type vocabulary to three values.
