---
name: cutlist
description: >
  Generate a cut list from cabinet units drawn in Blender or defined by dimensions.
  Use this skill whenever the user asks to extract a cut list, panel list, parts list,
  or material list from cabinet units. Requires the cabinet-specs skill for construction
  rules and banding specs. Produces a formatted Excel (.xlsx) file with all panels
  grouped into 3 sections: main carcass panels (18.5mm), back panels (7mm), and doors
  (18.5mm). Apply all rules below unless the user explicitly overrides a value.
---

# Cut List Generation — Workshop Standard

> This skill depends on **cabinet-specs** for panel thickness, banding rules, groove specs,
> and construction method. Always read cabinet-specs before generating a cut list.

---

## Step 1 — Extract Panel Dimensions from Blender

Pull all mesh object names and dimensions from the scene. Exclude:
- Appliances (e.g. fridge, oven)
- Decorative sub-units (prefix `U{n}D_`)
- Camera and light objects

```python
import bpy

exclude_prefixes = ["U1D_", "U1_Fridge", "OverviewCam", "Sun"]

for obj in bpy.data.objects:
    if obj.type != 'MESH': continue
    if any(obj.name.startswith(p) for p in exclude_prefixes): continue
    d = obj.dimensions
    # Sort dims descending to identify thickness (smallest = 1.85 or 0.7)
    dims = sorted([round(d.x,2), round(d.y,2), round(d.z,2)], reverse=True)
    print(f"{obj.name}: {dims[0]} x {dims[1]} x {dims[2]}")
```

The two relevant dimensions per panel are the two **largest** values.
The **smallest** value is always the thickness — exclude it from the cut list.

---

## Step 2 — Identify Unit Type per Panel

Determine whether each panel belongs to an **upper** or **lower** unit.
This affects banding rules.

| Unit | Type |
|---|---|
| Unit1 | Lower |
| Unit2 | Upper |
| Unit3 | Upper |
| Unit4 | Upper |
| Unit5 | Lower |

Identify unit type from the object name prefix: `U1_` → Unit 1, `U2_` → Unit 2, etc.

---

## Step 3 — Assign Length and Width

### Carcass Panels (all except doors)
- **Length** = bigger of the two dimensions
- **Width** = smaller of the two dimensions
- Reason: plywood sheet is 120 × 240cm — the long dimension of each panel
  runs parallel to the 240cm grain direction for maximum strength

### Door Panels
- **Length** = vertical/height dimension (parallel to 240cm grain direction)
- **Width** = horizontal dimension
- This may result in Length < Width for wide short doors — this is correct and intentional
- Door vertical dimension is always the Z axis value in Blender

---

## Step 4 — Grouping Identical Panels

Identical panels (same name pattern, same dimensions) must be **combined into one row**
with a quantity column instead of separate rows.

### Rules for grouping:
- Side panels: `U{n}_Side_L` + `U{n}_Side_R` → always identical → **qty: 2**
- Top + Bottom: `U{n}_Top` + `U{n}_Bot` → always identical → **qty: 2**
- Stretchers: group only if **both dimensions are identical**
  - `U{n}_Stretch_Front` and `U{n}_Stretch_Back` have the **same dimensions**
    but **different groove values** → must be **separate rows**
- Doors: group only if dimensions are identical
  - `U{n}_Door_L` + `U{n}_Door_R` → group if same size → **qty: 2**

### Label format for grouped rows:
```
U2_Side_L / U2_Side_R
U2_Top / U2_Bot
U2_Door_L / U2_Door_R
```

---

## Step 5 — Sections

The cut list is divided into **3 sections** in this order:

### Section 1 — Main Carcass Panels (18.5mm)
All structural panels except back panels and doors:
- Side panels, top, bottom, stretchers, shelves, dividers, inner panels
- Grouped by unit, with unit sub-headers

### Section 2 — Back Panels (7mm)
All back panels listed separately — different material thickness.
- One back panel per unit
- Grouped by unit

### Section 3 — Doors (18.5mm)
All doors from all units in one section.
- Use vertical dimension as Length (grain direction rule)
- Grouped by unit

---

## Step 6 — Columns

Every row must have exactly these **15 columns** in this order:

| # | Column | Type | Notes |
|---|---|---|---|
| 1 | **Unique Code** | string | Auto-generated from object name — see Step 6a |
| 2 | **Unit Name** | string | e.g. "Unit1_FridgeTall", "Unit2_Upper" |
| 3 | **Length** | number | cm, 2 decimal places |
| 4 | **Width** | number | cm, 2 decimal places |
| 5 | **Qty** | number | integer |
| 6 | **Material** | string | "18.5mm" or "7mm" |
| 7 | **Description** | string | Blender object name(s) — see grouping rules below |
| 8 | **Enabled** | boolean | Always `True` |
| 9 | **Grain Direction** | string | Always `"V"` |
| 10 | **Top Band (width)** | string | `"X"` if banded, `""` if not |
| 11 | **Left Band (length)** | string | `"X"` if banded, `""` if not |
| 12 | **Bottom Band (width)** | string | `"X"` if banded, `""` if not |
| 13 | **Right Band (length)** | string | `"X"` if banded, `""` if not |
| 14 | **Groove** | string | `"X"` if groove required, `""` if not |
| 15 | **Hinges** | string | `"X"` if hinges required, `""` if not |

### Description Column Rules

The Description is the **Blender object name**, directly from the scene naming convention.
Identical panels are **grouped into one row** with a combined label using ` / ` as separator.

#### Grouping rules — which panels merge into one row:

| Panels | Combined Label | Qty |
|---|---|---|
| `U1_Side_L` + `U1_Side_R` | `U1_Side_L / U1_Side_R` | 2 |
| `U1_Top` + `U1_Bot` (upper units only — identical dims) | `U1_Top / U1_Bot` | 2 |
| `U1_Door_L` + `U1_Door_R` | `U1_Door_L / U1_Door_R` | 2 |

#### Panels that are NEVER grouped (always separate rows):

| Panel | Reason |
|---|---|
| `Stretch_Front` | May differ from `Stretch_Back` on groove |
| `Stretch_Back` | Has groove — different from front |
| `Shelf` | One row per shelf even if multiple |
| `Back` | One per unit |
| `Drawer_1/2/3` | Different heights — never grouped |
| `Bot` on lower units | Not identical to any other panel |

#### Summary of all label patterns used:

```
# Upper units
U{n}_Side_L / U{n}_Side_R    ← grouped pair
U{n}_Top / U{n}_Bot           ← grouped pair (upper only — same dims)
U{n}_Shelf
U{n}_Back
U{n}_Door_L / U{n}_Door_R    ← grouped pair
U{n}_Door                     ← single door

# Lower/base units
U{n}_Side_L / U{n}_Side_R
U{n}_Bot                      ← NOT grouped with Top (lower units have no Top)
U{n}_Stretch_Front
U{n}_Stretch_Back
U{n}_Shelf
U{n}_Back
U{n}_Door_L / U{n}_Door_R
U{n}_Door
U{n}_Drawer_1
U{n}_Drawer_2
U{n}_Drawer_3

# Tall units
U{n}_Side_L / U{n}_Side_R
U{n}_Top / U{n}_Bot
U{n}_Shelf
U{n}_Divider
U{n}_Back
U{n}_Door_L / U{n}_Door_R
```

---

## Step 6a — Unique Code Generation

The Unique Code is derived from the **Description** (Blender object name) using first-letter initials.

### Rule
- Take the unit prefix as-is: `U1`, `U2`, etc.
- For each remaining word (split by `_`), take the **first letter only**
- For **grouped rows** (e.g. `U1_Side_L / U1_Side_R`), take the first letter of the
  **last token of each part** and combine them

### ⚠️ Collision Overrides (apply BEFORE the general rule)

Some panels produce identical codes under the general rule. These must use fixed overrides:

| Panel | General rule gives | Override code | Reason |
|---|---|---|---|
| `U{n}_Back` | `U{n}B` | **`U{n}BK`** | Collides with `U{n}_Bot` → `U{n}B` |
| `U{n}_Bot` | `U{n}B` | **`U{n}BT`** | Collides with `U{n}_Back` → `U{n}B` |
| `U{n}_Divider` | `U{n}D` | **`U{n}DV`** | Collides with `U{n}_Door` → `U{n}D` |

### Examples

| Description | Code | Logic |
|---|---|---|
| `U1_Side_L / U1_Side_R` | `U1SLR` | U1 + S(ide) + L + R |
| `U1_Top / U1_Bot` | `U1TB` | U1 + T(op) + B(ot) — grouped, no collision |
| `U1_Bot` | `U1BT` | override — would collide with U1BK |
| `U1_Stretch_Front` | `U1SF` | U1 + S(tretch) + F(ront) |
| `U1_Stretch_Back` | `U1SB` | U1 + S(tretch) + B(ack) |
| `U1_Shelf` | `U1S` | U1 + S(helf) |
| `U1_Back` | `U1BK` | override — would collide with U1BT |
| `U1_Door` | `U1D` | U1 + D(oor) |
| `U1_Divider` | `U1DV` | override — would collide with U1D |
| `U2_Door_L / U2_Door_R` | `U2DLR` | U2 + D(oor) + L + R |
| `U4_Door_Fixed` | `U4DF` | U4 + D(oor) + F(ixed) |
| `U5_Door_L` | `U5DL` | U5 + D(oor) + L |
| `U5_Drawer_1` | `U5D1` | U5 + D(rawer) + 1 |

### Python Implementation

```python
# Fixed overrides for known collisions
OVERRIDES = {
    "_Back":    "BK",   # U1_Back  → U1BK  (not U1B, which is U1_Bot)
    "_Bot":     "BT",   # U1_Bot   → U1BT  (not U1B, which is U1_Back)
    "_Divider": "DV",   # U1_Divider → U1DV (not U1D, which is U1_Door)
}

def make_code(desc):
    parts = [p.strip() for p in desc.split(' / ')]
    first = parts[0]
    unit = first.split('_')[0]   # e.g. 'U1'
    suffix = first[len(unit):]   # e.g. '_Back' or '_Side_L'

    # Check overrides first
    for key, override in OVERRIDES.items():
        if suffix == key:
            return unit + override

    # General rule: first letter of each word token after unit prefix
    tokens = first.split('_')
    initials = [t[0] for t in tokens[1:]]
    if len(parts) > 1:
        last_tokens = [p.split('_')[-1][0] for p in parts]
        initials = initials[:-1] + last_tokens
    return unit + ''.join(initials)
```

---

## Step 7 — Banding Rules

Apply banding based on **unit type** and **panel type**.
See cabinet-specs for full edge banding spec. Summary:

### Upper Units — Carcass
| Panel | Top | Left | Bottom | Right |
|---|---|---|---|---|
| Side panels | ✓ | ✓ | ✓ | ✗ |
| Top panel | ✗ | ✓ | ✗ | ✗ |
| Bottom panel | ✗ | ✓ | ✗ | ✗ |
| Shelves | ✗ | ✓ | ✗ | ✗ |
| Dividers / Inner panels | ✗ | ✓ | ✗ | ✗ |

### Lower Units — Carcass
| Panel | Top | Left | Bottom | Right |
|---|---|---|---|---|
| Side panels | ✗ | ✓ | ✗ | ✗ |
| Stretchers | ✗ | ✓ | ✗ | ✗ |
| Bottom panel | ✗ | ✓ | ✗ | ✗ |
| Shelves | ✗ | ✓ | ✗ | ✗ |
| Dividers / Inner panels | ✗ | ✓ | ✗ | ✗ |

### Back Panels (all unit types)
| Top | Left | Bottom | Right |
|---|---|---|---|
| ✗ | ✗ | ✗ | ✗ |

### Doors (all unit types)
| Top | Left | Bottom | Right |
|---|---|---|---|
| ✓ | ✓ | ✓ | ✓ |

> **Note:** "Left Band" corresponds to the **front-facing edge** of carcass panels.
> Dividers and inner panels: only the face **visible to the user** (front face) gets banding → Left only.

---

## Step 8 — Groove Rules

Groove = back panel groove (8mm wide × 8mm deep, 19mm from back edge).

| Panel | Groove |
|---|---|
| Side panels | ✓ |
| Top panel | ✓ |
| Bottom panel | ✓ |
| Front Stretcher | ✗ |
| Back Stretcher | ✓ — aligns with back panel groove on side panels |
| Shelves | ✗ |
| Dividers | ✗ |
| Inner panels | ✗ |
| Back panels | ✗ |
| Doors | ✗ |

---

## Step 9 — Hinges Rules

| Panel | Hinges |
|---|---|
| Doors | ✓ |
| All other panels | ✗ |

---

## Step 10 — Output Files

Always produce **two files**:

### File 1 — `cutlist.xlsx`
Formatted Excel with 3 sections, unit sub-headers, colour coding, and all 15 columns.

Use **openpyxl** to produce the formatted .xlsx file.

#### Sheets
1. **Cut List** — main data sheet with all 3 sections
2. **Summary** — totals by section (unique rows + total qty)

#### Styling
- Header row: dark background (`#37474F`), white bold Arial font
- **No merged cells anywhere** — section and unit headers span only column 1, all other columns in that row are styled but empty
- Section separator rows: coloured background, label in column 1 only
  - Section 1 (Main): `#E65100` orange
  - Section 2 (Back): `#1565C0` blue
  - Section 3 (Doors): `#6A1B9A` purple
- Unit sub-header rows: light grey `#ECEFF1`, bold italic, label in column 1 only
- Data rows: light tint matching section colour
  - Section 1: `#FFF3E0`
  - Section 2: `#E3F2FD`
  - Section 3: `#F3E5F5`
- All cells: thin border `#CCCCCC`
- Freeze top row
- Column widths: auto-sized to content

---

### File 2 — `cutlist_optimizer_input.csv`
Flat CSV for optimizer software — **no section headers, no unit sub-headers, data rows only**.

#### Columns (11 only — in this exact order):
```
Length, Width, Qty, Material, Description, Enabled, Grain Direction,
Top Band, Left Band, Bottom Band, Right Band
```

> ⚠️ **Column naming:** The Description column in this CSV uses the name **`Description`**
> (not `Label`, not `Unique Code`). It contains the Blender object name
> e.g. `U1_Side_L / U1_Side_R`.

> ⚠️ **Band values:** Use `X` or empty string `""` — never `None`, `True`, or `False`.

#### Python implementation:
```python
import csv

csv_headers = [
    "Length","Width","Qty","Material","Description",
    "Enabled","Grain Direction",
    "Top Band","Left Band","Bottom Band","Right Band"
]

def v(val):
    """Convert None/False to empty string, True stays True, X stays X."""
    return val if val else ""

with open("cutlist_optimizer_input.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(csv_headers)
    for row in all_rows:
        # row = [unit_name, length, width, qty, material, description,
        #         enabled, grain, top_band, left_band, bot_band, right_band, groove, hinges]
        writer.writerow([
            row[1],      # Length
            row[2],      # Width
            row[3],      # Qty
            row[4],      # Material
            row[5],      # Description (object name)
            row[6],      # Enabled
            row[7],      # Grain Direction
            v(row[8]),   # Top Band
            v(row[9]),   # Left Band
            v(row[10]),  # Bottom Band
            v(row[11]),  # Right Band
        ])
```

### File 3 — `cutlist_full.csv`
Full CSV export of all data rows — 14 columns (all xlsx columns except Unit Name), no styling, no section headers, no unit sub-headers.

#### Columns (14 — xlsx order minus Unit Name):
```
Unique Code, Length, Width, Qty, Material, Description, Enabled, Grain Direction,
Top Band (width), Left Band (length), Bottom Band (width), Right Band (length), Groove, Hinges
```

#### Python implementation:
```python
import csv

csv_full_headers = [
    "Unique Code","Length","Width","Qty","Material","Description",
    "Enabled","Grain Direction",
    "Top Band (width)","Left Band (length)","Bottom Band (width)","Right Band (length)",
    "Groove","Hinges"
]

with open("cutlist_full.csv","w",newline="",encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(csv_full_headers)
    for row in rows:   # rows = all data rows (main + back + doors)
        full_row = [make_code(row[5])] + row
        writer.writerow([
            full_row[0],          # Unique Code
            full_row[2],          # Length      ← skip Unit Name (full_row[1])
            full_row[3],          # Width
            full_row[4],          # Qty
            full_row[5],          # Material
            full_row[6],          # Description
            full_row[7],          # Enabled
            full_row[8],          # Grain Direction
            v(full_row[9]),       # Top Band (width)
            v(full_row[10]),      # Left Band (length)
            v(full_row[11]),      # Bottom Band (width)
            v(full_row[12]),      # Right Band (length)
            v(full_row[13]),      # Groove
            v(full_row[14]),      # Hinges
        ])
```

---

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

wb = Workbook()
ws = wb.active
ws.title = "Cut List"

T = True; F = False

def make_code(label):
    parts = [p.strip() for p in label.split(' / ')]
    tokens = parts[0].split('_')
    unit = tokens[0]
    initials = [t[0] for t in tokens[1:]]
    if len(parts) > 1:
        last_tokens = [p.split('_')[-1][0] for p in parts]
        initials = initials[:-1] + last_tokens
    return unit + ''.join(initials)

# Each row: [unit_name, length, width, qty, material, description,
#            enabled, grain, top_band, left_band, bot_band, right_band, groove, hinges]
# description = Blender object name e.g. "U1_Side_L / U1_Side_R"
# Unique Code is prepended automatically when writing: [make_code(row[5])] + row
rows = []

# ... populate rows here ...

headers = [
    "Unique Code","Unit Name","Length","Width","Qty","Material","Description",
    "Enabled","Grain Direction",
    "Top Band (width)","Left Band (length)","Bottom Band (width)","Right Band (length)",
    "Groove","Hinges"
]

# Write headers
ws.append(headers)
# When writing data rows, prepend the unique code and convert banding/groove/hinge:
#   full_row = [make_code(row[5])] + row   ← row[5] is Description (object name)
#   for cols >= 11: cell.value = xval(val)  ← "X" or ""
# ⚠️ NEVER use ws.merge_cells() — no merged cells anywhere in the sheet

wb.save("cutlist.xlsx")

# ── File 2: CSV for optimizer ──────────────────────────────────────────────
import csv

def v(val): return val if val else ""

csv_headers = [
    "Length","Width","Qty","Material","Description",
    "Enabled","Grain Direction",
    "Top Band","Left Band","Bottom Band","Right Band"
]

with open("cutlist_optimizer_input.csv","w",newline="",encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(csv_headers)
    for row in rows:   # rows = all data rows (main + back + doors)
        writer.writerow([
            row[1], row[2], row[3], row[4], row[5],
            row[6], row[7],
            v(row[8]), v(row[9]), v(row[10]), v(row[11]),
        ])
```

---

## Column Widths (approximate)

| Col | Width |
|---|---|
| Unique Code | 12 |
| Unit Name | 22 |
| Length | 10 |
| Width | 10 |
| Qty | 6 |
| Material | 12 |
| Description | 38 |
| Enabled | 9 |
| Grain Direction | 16 |
| Top/Left/Bottom/Right Band | 14–16 each |
| Groove | 9 |
| Hinges | 9 |

```python
def xval(v):
    """Convert boolean to 'X' or '' for banding/groove/hinge columns."""
    return "X" if v else ""

def get_banding(panel_type, unit_type):
    # Returns (top, left, bottom, right) as "X" or ""
    if "Door" in panel_type:
        return ("X", "X", "X", "X")
    if "Back" in panel_type:
        return ("",  "",  "",  "")
    if unit_type == "upper":
        if "Side" in panel_type: return ("X", "X", "X", "")
        # Top, Bot, Shelves, Dividers, Inner panels
        return ("", "X", "", "")
    if unit_type == "lower":
        # Side, Stretcher, Bot, Shelf, Divider all: front only
        return ("", "X", "", "")
    return ("", "", "", "")

def get_groove(panel_type):
    grooved = ["Side", "Top", "Bot", "Stretch_Back"]
    return "X" if any(g in panel_type for g in grooved) else ""

def get_hinges(panel_type):
    return "X" if "Door" in panel_type else ""
```

---

## Common Mistakes to Avoid

1. **Do NOT use thickness as a dimension** — always drop the smallest of the 3 dimensions
2. **Do NOT apply the bigger=length rule to doors** — doors always use vertical=length
3. **Do NOT group Stretch_Front and Stretch_Back** — they differ on groove
4. **Do NOT include decorative sub-units** (U{n}D_ prefix) unless explicitly requested
5. **Do NOT include appliances** (fridge, oven etc.) — they are not cut panels
6. **Do NOT forget the back stretcher groove** — it is easily missed
7. **Always extract dimensions from Blender directly** — do not rely on nominal unit dimensions,
   as actual panel sizes include construction offsets (IW, IH etc.)
8. **Do NOT use merged cells anywhere** — section headers and unit sub-headers have their
   label in column 1 only; all other columns in that row are styled but left empty
9. **Always produce all three files** — `cutlist.xlsx`, `cutlist_optimizer_input.csv`, `cutlist_full.csv`
10. **CSV Description column** — must be named `Description` (not Label, not Unique Code);
    contains the Blender object name e.g. `U1_Side_L / U1_Side_R`
11. **CSV band values** — use `X` or `""` only — never `None`, `True`, or `False`
