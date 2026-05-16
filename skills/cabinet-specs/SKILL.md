---
name: cabinet-specs
description: >
  Cabinet construction specifications for a custom kitchen/furniture workshop.
  Use this skill whenever the user asks to define, validate, calculate, or build
  cabinet units — including base units, upper units, sink bases, drawer units,
  or any carcass with doors or drawers. Also trigger when generating cut lists,
  calculating door sizes, drawer door sizes, drawer body panels, shelf sizes,
  back panels, grooves, slide hardware clearances, or edge banding for cabinet
  work. Apply these specs as the default standard for ALL cabinet-related tasks
  unless the user explicitly overrides a value.
---

# Cabinet Specifications — Workshop Standard

## Material & Panel Thickness
- **Material:** Countertop panel (كونتر)
- **Panel thickness:** 18.55mm
- **Back panel thickness:** 7mm
- **Edge banding:** 1mm PVC

---

## Kitchen Unit Categories

Every kitchen unit belongs to one of three categories:

| Category | Description | Drawers Allowed? |
|---|---|---|
| **lower** | Base units below the countertop | ✓ Yes |
| **mid-upper** | Upper units at mid-height (typically over countertop, reachable) | ✗ No |
| **high-upper** | Upper units at high height (above mid-uppers, harder to reach) | ✗ No |

> Drawers exist **only in lower units**. Mid-upper and high-upper units are doors only.

---

## Handle Type Modifiers

Doors and drawer doors get a height adjustment based on unit category and handle type.
The modifier is applied to `unit_height` **first**, then the standard banding/clearance
formulas run on the resulting `effective_height`.

| Category | Handle Type | Height Modifier | Applied To |
|---|---|---|---|
| **lower** | Standard pulls | none | — |
| **lower** | Integrated groove handle | **−30mm PER door/drawer** (from top) | Each door and each drawer individually |
| **mid-upper** | Standard pulls | none | — |
| **mid-upper** | No pulls (door acts as handle) | **+20mm** (extends below carcass, once per stack) | Bottom-most door only |
| **high-upper** | Any | none | — |

```
# Lower with groove handle (per-door deduction):
effective_height = unit_height − (N × 30mm)
  where N = number of doors AND drawer fronts in the unit

# Mid-upper no-pull (single deduction at bottom):
effective_height = unit_height + 20mm
  (only the bottom-most door extends; stacked doors above don't add another 20mm)
```

> Modifiers are **mutually exclusive per unit** and only apply when there are no separate pulls.

---

## Key Calculations

```
inner_width  = total_width  − (panel_thickness × 2)
             = total_width  − 37mm

inner_height = total_height − (panel_thickness × 2)
             = total_height − 37mm

inner_shelf_width = total_width − ((panel_thickness × 2) + 1mm)
                  = total_width − 38mm

inner_shelf_depth = unit_depth − 30mm
```

### Divider Sizing

Dividers are vertical panels that split the interior of a unit into bays.

```
divider_depth  = unit_depth − 30mm      (workshop standard, same as shelf depth)
divider_height = inner_height            (= total_height − 37mm)
divider_width  = specified per unit definition
                 (for equal bays: inner_width / number_of_bays, rounded to 0.5mm)
```

> For multi-bay layouts, bay widths must be explicitly specified in the unit definition.
> The platform does not infer bay widths from unit width alone.

---

## Construction Method

### Side Panels
- Always **OUTSIDE** — full height, covering top and bottom panels on both unit types.

### Upper Units
- **Top (قرصة)** and **Bottom (قاعدة):** INSIDE between sides
- Width of top/bottom = `inner_width`

### Lower Units
- **Bottom panel (قاعدة):** INSIDE between sides
- Width of bottom = `inner_width`
- **NO full top panel** — replaced by two stretchers:
  - Front Stretcher + Back Stretcher
  - Each: 100mm deep × `inner_width` wide × 18.55mm thick
  - Both flush with top edge of side panels

---

## Back Panel

| Property | Value |
|---|---|
| Thickness | 7mm |
| Width | `inner_width + 16mm` |
| Height | `inner_height + 16mm` |
| Mounting | Sits inside groove on all 4 panels |

### Groove Specs
| Property | Value |
|---|---|
| Groove width | 8mm |
| Groove depth | 8mm |
| Distance from back edge | 19mm |
| Cut into | Both sides + top + bottom panels + back stretcher (lower units) |

---

## Edge Banding (1mm PVC)

### Doors & Drawer Fronts
- All **4 edges** banded

### Upper Units — Carcass
| Panel | Edges |
|---|---|
| Side panels | Front + Bottom + Top |
| Top panel (قرصة) | Front only |
| Bottom panel (قاعدة) | Front only |

### Lower Units — Carcass
| Panel | Edges |
|---|---|
| Side panels | Front only |
| Stretchers | Front only |
| Bottom panel (قاعدة) | Front only |

---

## Doors — Overlay

### Clearances
| Gap | Value |
|---|---|
| Top | 2mm |
| Bottom | 2mm |
| Between doors (center) | 1mm per door = 2mm total for 2 doors |

### Door Size Formula

> ⚠️ These are **raw cut sizes** (before banding). Banding is applied after cutting.
> ⚠️ `effective_height` = `unit_height + handle_modifier` (see Handle Type Modifiers above).
> For units with no modifier, `effective_height = unit_height`.
> ⚠️ `unit_height` = **side panel length** (the carcass side's vertical dimension), NOT the
> overall cabinet bounding-box height. For a lower unit with toe-kick, the side panel
> length is typically 750mm even though the unit envelope is 850mm tall.

```
door_width = ( total_width
               − (2mm × number_of_doors)          ← side + center gaps
               − (2 × banding × number_of_doors)  ← banding both sides of each door
             ) / number_of_doors

door_height = effective_height
              − (2 × banding)      ← top + bottom banding
              − 2mm                ← vertical clearance (top + bottom gaps)
```

### Worked Example — 850 × 450 unit, 2 doors

```
door_width  = (850 − (2×2) − (2×1×2)) / 2
            = (850 − 4 − 4) / 2
            = 842 / 2
            = 421mm

door_height = 450 − (2×1) − 2
            = 450 − 2 − 2
            = 446mm
```

### General Table

| N doors | Total width gap | door_width formula |
|---|---|---|
| 1 | 1×2 + 2×1×1 = 4mm | (W − 4) / 1 |
| 2 | 2×2 + 2×1×2 = 8mm | (W − 8) / 2 |
| 3 | 3×2 + 2×1×3 = 12mm | (W − 12) / 3 |
| 4 | 4×2 + 2×1×4 = 16mm | (W − 16) / 4 |

**Simplified:** `door_width = (W − N × 4mm) / N`

---

### Corner Cabinets

A corner cabinet has **two independent door faces at 90°** (one on the W-axis face,
one on the D-axis face). The unit's bounding width is the diagonal extent, so the
standard `(W − N×4)/N` formula does not apply to either face.

**Door width rule:**

Corner cabinet door widths **must be explicitly specified per face** in the unit definition
(`face_width_L` and `face_width_R`). They cannot be derived from total unit width because
each face's opening depends on the L/R configuration of the corner.

**Door height:** Uses the standard formula — both faces share the same opening height.

```
door_height (both faces) = effective_height − (2 × banding) − 2mm
```

Each corner door is a **separate row** in the cut list (qty 1 each), since L and R
doors have different widths. Heights match because they share the same opening.

> For rectangular units (non-corner), always use the `(W − N×4)/N` formula.
> Explicit face widths apply only to corner units.

---

## Wood Grain Direction
- **All door panels:** Vertical (↕️)
- **All drawer outer panels:** Vertical (↕️)

---

## Quick Reference — Python

```python
T  = 18.55  # panel thickness mm
EB = 1.0    # edge banding mm

# Handle modifiers
MOD_MID_UPPER_NO_PULL = +20   # door extends 20mm below carcass
MOD_LOWER_GROOVE      = -30   # door shortened 30mm from top

def effective_height(H, category, handle):
    """
    category: 'lower' | 'mid-upper' | 'high-upper'
    handle:   'pulls' | 'none' | 'groove'
    """
    if category == 'mid-upper' and handle == 'none':
        return H + MOD_MID_UPPER_NO_PULL
    if category == 'lower' and handle == 'groove':
        return H + MOD_LOWER_GROOVE
    return H  # high-upper, or lower/mid-upper with standard pulls

def inner_width(W):    return W - 2*T
def inner_height(H):   return H - 2*T
def shelf_width(W):    return W - (2*T + 1)
def shelf_depth(D):    return D - 30
def divider_depth(D):  return D - 30    # same as shelf depth
def divider_height(H): return inner_height(H)

def back_panel(W, H):
    return inner_width(W) + 16, inner_height(H) + 16

def door_width(W, N):
    return (W - N * 2 - 2 * EB * N) / N

def door_height(H, category='lower', handle='pulls'):
    H_eff = effective_height(H, category, handle)
    return H_eff - 2*EB - 2

# Example — standard lower unit with pulls
W, H, N = 850, 450, 2
print(f"Door: {door_width(W,N):.1f} × {door_height(H):.1f} mm")
# → Door: 421.0 × 446.0 mm

# Example — mid-upper, no pulls (door acts as handle)
print(f"Mid-upper no-pull door height: {door_height(450, 'mid-upper', 'none'):.1f} mm")
# → 466.0 mm  (450 + 20 − 2 − 2)

# Example — lower with integrated groove handle
print(f"Lower groove door height: {door_height(720, 'lower', 'groove'):.1f} mm")
# → 686.0 mm  (720 − 30 − 2 − 2)
```

---

# Drawer Specifications

> Drawers exist **only in lower units**. Mid-upper and high-upper units do not have drawers.

## Drawer Types

| Type | Slide Hardware | Notes |
|---|---|---|
| **Side Slides** | Rails mounted on left & right sides of body | Standard, most common |
| **Bottom Slides** | Rail mounted under drawer body | Requires less side clearance |

---

## A — Internal Drawer Body (4 Panels)

All internal body panels are cut from **18.55mm panel** (same material as carcass).

### Panel Heights (all 4 sides share the same height)

```
drawer_body_height = drawer_door_height − 20mm
```

> Applies to **both side-slide and bottom-slide** drawers.
> The 20mm deduction accounts for clearance above and below the body inside the unit.

### 1. Depth Panels (2 panels — run perpendicular to door, i.e. into the unit)

Length is **always 450mm** regardless of unit depth (workshop standard for drawer slide hardware).

```
depth_panel_length = 450mm   (always 450mm)
```

> ⚠️ This is fixed even if the unit_depth is larger (e.g. 500mm or 600mm deep units).
> The drawer body sits inside the unit at 450mm, leaving room at the back for the
> back panel groove + service space. The drawer slide hardware is sized to 450mm runners.

### 2. Width Panels (2 panels — run parallel to the door)

Length depends on slide type:

#### Side Slides
```
width_panel_length = unit_width − (T×2 + T×2 + 25)
                   = unit_width − (37 + 37 + 25)
                   = unit_width − 99mm

where:
  T×2 = 37mm  →  2 unit side panels (left + right carcass sides)
  T×2 = 37mm  →  2 drawer depth panels (left + right body sides)
  25mm        →  slide hardware clearance (12.5mm per side)
```

#### Bottom Slides
```
width_panel_length = unit_width − (T×2 + T×2 + 6)
                   = unit_width − (37 + 37 + 6)
                   = unit_width − 80mm

where:
  T×2 = 37mm  →  2 unit side panels
  T×2 = 37mm  →  2 drawer depth panels
  6mm         →  bottom slide hardware clearance (3mm per side)
```

### Edge Banding — Drawer Body Panels

| Panel | Banded Edges |
|---|---|
| Depth panels (×2) | Top edge only |
| Width panels (×2) | Top edge only |

> Bottom and side edges of body panels are hidden inside the unit or against slides.

---

## B — External Drawer Door

Drawer doors are always banded on **all 4 edges** (same as hinged doors).
Wood grain direction: **Vertical (↕️)**

### Positioning Types

| Type | Door Position | Typical Use |
|---|---|---|
| **Outer drawer** | Door face is flush with carcass front face | Matches hinged doors in a run |
| **Inner drawer** | Door sits recessed inside the carcass opening | Inset / frameless look |

---

### Case 1 — Outer Drawer Door

```
door_height = unit_height
              − (N × 2mm)          ← edge banding top+bottom per door (1mm × 2 per door)
              − (N − 1) × 2mm      ← clearance gaps between doors
              − (N × 30mm)         ← ONLY IF handle = groove (every drawer shortened individually)

door_width  = unit_width − 2mm     ← 1mm edge banding each side
```

Where **N** = number of drawers in the unit.

> Groove handle (−30mm) is deducted **per drawer**, from the top of each individual
> drawer door. For 3 drawers with groove handle, total height deduction = 90mm.

**Example — 720mm tall unit, 3 drawers, standard pulls:**
```
door_height = 720 − (3×2) − (2×2)
            = 720 − 6 − 4
            = 710mm  → each drawer door height = 710 / 3 ≈ 236.7mm

door_width  = unit_width − 2mm
```

**Example — 720mm tall unit, 3 drawers, integrated groove handle:**
```
door_height = 720 − (3×2) − (2×2) − (3×30)
            = 720 − 6 − 4 − 90
            = 620mm  → each drawer door height = 620 / 3 ≈ 206.7mm
```

---

### Case 2 — Inner Drawer Door

```
door_height = unit_height
              − (N × 2mm)              ← edge banding per door
              − (N − 1) × 2mm         ← clearance gaps between doors
              − (T × 2)               ← carcass top + bottom panels (inset offset)
              − (N × 30mm)            ← ONLY IF handle = groove (every drawer shortened individually)

door_width  = unit_width
              − 2mm                   ← edge banding
              − (T × 2)               ← carcass left + right sides (inset offset)
            = unit_width − 2 − 37
            = unit_width − 39mm

where T = 18.55mm panel thickness
```

---

### Drawer Door Size — Summary Table

| | Outer | Inner |
|---|---|---|
| **Height (pulls)** | `H − N×2 − (N−1)×2` | `H − N×2 − (N−1)×2 − T×2` |
| **Height (groove)** | `H − N×2 − (N−1)×2 − N×30` | `H − N×2 − (N−1)×2 − T×2 − N×30` |
| **Width** | `W − 2` | `W − 2 − T×2` |

> All sizes are **raw cut sizes** (before banding). Banding is applied after cutting.
> Groove handle deducts 30mm **per drawer** (from the top of each drawer door individually).

---

## Quick Reference — Python (Drawers)

```python
T  = 18.55  # panel thickness mm
EB = 1.0    # edge banding mm
SLIDE_SIDE   = 25.0  # side slide hardware clearance (total both sides)
SLIDE_BOTTOM = 6.0   # bottom slide hardware clearance (total both sides)
GROOVE_MOD   = 30.0  # lower-unit groove handle deduction per drawer

def drawer_body_height(door_height):
    # Same rule for both side-slide and bottom-slide drawers
    return door_height - 20

def drawer_depth_panel(unit_depth=None):
    """Fixed 450mm regardless of unit_depth (workshop standard for drawer slides)."""
    return 450

def drawer_width_panel_side_slides(unit_width):
    return unit_width - (T*2 + T*2 + SLIDE_SIDE)   # −99mm

def drawer_width_panel_bottom_slides(unit_width):
    return unit_width - (T*2 + T*2 + SLIDE_BOTTOM)  # −80mm

def outer_drawer_door(unit_width, unit_height, N, handle='pulls'):
    """N = number of drawers. Drawers are lower-unit only.
       handle: 'pulls' | 'groove'"""
    groove = N * GROOVE_MOD if handle == 'groove' else 0
    h = unit_height - (N * 2*EB) - (N - 1) * 2 - groove
    w = unit_width - 2*EB
    return w, h / N  # per-door dimensions

def inner_drawer_door(unit_width, unit_height, N, handle='pulls'):
    groove = N * GROOVE_MOD if handle == 'groove' else 0
    h = unit_height - (N * 2*EB) - (N - 1) * 2 - T*2 - groove
    w = unit_width - 2*EB - T*2
    return w, h / N

# Example — 600mm wide, 720mm tall unit, 3 outer drawers, side slides, pulls
W, H, N = 600, 720, 3
door_w, door_h = outer_drawer_door(W, H, N, handle='pulls')
body_h = drawer_body_height(door_h)
body_w = drawer_width_panel_side_slides(W)

print(f"Door:        {door_w:.1f} × {door_h:.1f} mm")
print(f"Body height: {body_h:.1f} mm")
print(f"Depth panel: 450 × {body_h:.1f} mm  (×2, fixed 450mm regardless of unit depth)")
print(f"Width panel: {body_w:.1f} × {body_h:.1f} mm  (×2)")

# Same unit but with integrated groove handle
door_w_g, door_h_g = outer_drawer_door(W, H, N, handle='groove')
print(f"Groove door: {door_w_g:.1f} × {door_h_g:.1f} mm  (30mm shorter each)")
```

---

## Part Naming Convention — Drawers

```
U{n}_Drawer{d}_Door          — outer door panel of drawer d
U{n}_Drawer{d}_Side_L        — left depth panel (perpendicular to door)
U{n}_Drawer{d}_Side_R        — right depth panel
U{n}_Drawer{d}_Front         — inner front width panel (parallel to door)
U{n}_Drawer{d}_Back          — inner back width panel
```

Where `{n}` = unit number, `{d}` = drawer number from top (1 = topmost drawer).

---

## Part Naming Convention

Use this consistent naming pattern for all panel parts. This naming maps directly
to the **Description** column in the cut list and to the platform's part label schema.

```
U{n}_Side_L            — left side panel
U{n}_Side_R            — right side panel
U{n}_Top               — top panel
U{n}_Bot               — bottom panel
U{n}_Stretch_Front     — front stretcher (lower units) — no groove
U{n}_Stretch_Back      — back stretcher (lower units)  — has groove
U{n}_Shelf             — shelf (add _2, _3 for multiple shelves)
U{n}_Back              — back panel (7mm)
U{n}_Door              — single door
U{n}_Door_L            — left door of a pair
U{n}_Door_R            — right door of a pair
U{n}_Door_Fixed        — non-opening fixed door panel
U{n}_Door_Open_L/R     — opening doors
U{n}_Divider           — internal vertical divider
U{n}_InnerPanel_L/R    — structural wing panels attached to sides
U{n}D_                 — prefix for decorative sub-unit panels (excluded from cut list)
```

Where `{n}` = unit number (1, 2, 3 ...).
