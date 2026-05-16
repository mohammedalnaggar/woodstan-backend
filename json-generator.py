"""Blender scene extraction → scene_data.json for the cut list builder.

Run this inside Blender (Scripting tab, or via Blender's --python flag, or via MCP).

What it does:
  1. Finds every Cabinet.* parent in the scene, classifies by Z position:
       z < 0.5m  → lower
       z < 1.9m  → mid-upper
       else      → high-upper
     Orders within each category by (Y, X) location and assigns U1..UN.
  2. Renames every panel descendant under each cabinet to U{n}_<Suffix>.
     Hardware/visualizer meshes (pulls, knobs, leg levelers, Bay, Opening,
     Doors group, Drawers group, etc.) are skipped.
  3. Synthesizes drawer body panels (2 depth + 2 width) for every DrawerFront
     found, using the workshop rules:
       body_h = drawer_front_height − 20mm
       depth_panel: 450mm × body_h × 1.85cm (fixed 450mm)
       width_panel: (unit_W − 80mm) × body_h × 1.85cm  (bottom slides)
  4. Writes scene_data.json to ~/Desktop/scene_data.json.

Output format:
  {
    "units": { "1": {"category": "lower", "size_cm": [W, D, H]}, ... },
    "panels": [
      { "name": "U1_Side_L", "unit": 1, "suffix": "Side_L",
        "dims_sorted_desc": [L, W, T] },
      ...
    ]
  }
"""
import bpy
import json
import re
import os

# ============================================================
# Step 1: Find Cabinet parents, categorize and order
# ============================================================
cabs = [o for o in bpy.data.objects if o.name.startswith('Cabinet') and o.type == 'MESH']

def categorize(cab):
    z = cab.location.z
    if z < 0.5:  return 'lower'
    if z < 1.9:  return 'mid-upper'
    return 'high-upper'

lowers      = sorted([c for c in cabs if categorize(c) == 'lower'],
                     key=lambda c: (c.location.y, c.location.x))
mid_uppers  = sorted([c for c in cabs if categorize(c) == 'mid-upper'],
                     key=lambda c: (c.location.y, c.location.x))
high_uppers = sorted([c for c in cabs if categorize(c) == 'high-upper'],
                     key=lambda c: (c.location.y, c.location.x))
ordered = lowers + mid_uppers + high_uppers

unit_meta = {
    str(i): {
        'category': categorize(c),
        'size_cm': [round(c.dimensions.x * 100, 1),
                    round(c.dimensions.y * 100, 1),
                    round(c.dimensions.z * 100, 1)],
    }
    for i, c in enumerate(ordered, 1)
}
unit_width_cm = {int(k): v['size_cm'][0] for k, v in unit_meta.items()}

print(f"Cabinets found: {len(cabs)}")
print(f"  Lower:      {len(lowers)}")
print(f"  Mid-upper:  {len(mid_uppers)}")
print(f"  High-upper: {len(high_uppers)}")

# ============================================================
# Step 2: Rename all panel descendants to U{n}_<Suffix>
# ============================================================
def classify_child(child_name):
    """Map a Cabinet Designer child mesh name → cut-list suffix, or None to skip."""
    base = re.sub(r'\.\d+$', '', child_name).strip()
    b = base.lower()
    # SKIP: hardware, visualizer, environment
    if b in ('pull', 'pull 8in (203mm) bar', 'round knob'): return None
    if b.startswith('leg leveler'): return None
    if b in ('bay', 'interior', 'doors', 'drawers'): return None
    if b.startswith('opening'): return None
    if b in ('open with shelves', 'pullout', 'appliance', 'wall', 'floor'): return None
    if b == 'corner overlay calc': return None
    # CARCASS
    if b == 'top': return 'Top'
    if b == 'bottom': return 'Bot'
    if b == 'left side': return 'Side_L'
    if b == 'right side': return 'Side_R'
    if b == 'back': return 'Back'
    if b == 'left back': return 'Back_L'
    if b == 'right back': return 'Back_R'
    if b == 'left panel': return 'InnerPanel_L'
    if b == 'right panel': return 'InnerPanel_R'
    if b == 'front stretcher': return 'Stretch_Front'
    if b == 'back stretcher': return 'Stretch_Back'
    if b == 'shelf': return 'Shelf'
    if b == 'splitter vertical' or b.startswith('vertical splitter'): return 'Divider_V'
    if b == 'splitter horizontal' or b.startswith('horizontal splitter'): return 'Divider_H'
    if b == 'applied end left':  return 'ApplEnd_L'
    if b == 'applied end right': return 'ApplEnd_R'
    if b == 'applied end back':  return 'ApplEnd_Back'
    # DOORS
    if b == 'left door': return 'Door_L'
    if b == 'right door': return 'Door_R'
    if b == 'flip up door': return 'Door_FlipUp'
    # DRAWER FRONTS
    if b == 'drawer box': return 'DrawerBox'
    if b == 'drawer front' or b == 'front': return 'DrawerFront'
    if b == 'sink apron': return 'SinkApron'
    if b == 'false front': return 'FalseFront'
    return None  # unknown → skip silently

def all_descendants(obj):
    result = []
    def walk(o):
        for c in o.children:
            result.append(c)
            walk(c)
    walk(obj)
    return result

u_prefix = re.compile(r'^U\d+_')
rename_plan = {}
for u_num, cab in enumerate(ordered, 1):
    suffix_count = {}
    for child in all_descendants(cab):
        if child.type != 'MESH': continue
        if u_prefix.match(child.name): continue  # already renamed, skip
        sfx = classify_child(child.name)
        if sfx is None: continue
        suffix_count[sfx] = suffix_count.get(sfx, 0) + 1
        new_name = f'U{u_num}_{sfx}' if suffix_count[sfx] == 1 \
                   else f'U{u_num}_{sfx}_{suffix_count[sfx]}'
        rename_plan[child.name] = new_name

# Two-pass rename (temp prefix to avoid collisions)
TMP = "__TMP_RENAME__"
renamed = 0
for old, new in rename_plan.items():
    obj = bpy.data.objects.get(old)
    if obj is None: continue
    obj.name = TMP + new
    renamed += 1
for obj in list(bpy.data.objects):
    if obj.name.startswith(TMP):
        obj.name = obj.name[len(TMP):]
print(f"Renamed {renamed} panels")

# ============================================================
# Step 3: Extract panel data from Blender
# ============================================================
panels = []
for obj in bpy.data.objects:
    if obj.type != 'MESH': continue
    m = re.match(r'^U(\d+)_(.+)$', obj.name)
    if not m: continue
    d = obj.dimensions
    x_cm = round(d.x * 100, 2)
    y_cm = round(d.y * 100, 2)
    z_cm = round(d.z * 100, 2)
    panels.append({
        'name': obj.name,
        'unit': int(m.group(1)),
        'suffix': m.group(2),
        'dims_xyz_cm': [x_cm, y_cm, z_cm],          # raw axes (X=height for fronts)
        'dims_sorted_desc': sorted([x_cm, y_cm, z_cm], reverse=True),  # legacy / for non-front panels
    })

print(f"Real Blender panels extracted: {len(panels)}")

# ============================================================
# Step 4: Synthesize drawer body panels (4 per drawer)
#
# Rules (workshop convention):
#   body_h          = drawer_front_height − 20mm
#   depth_panel × 2 = 450mm × body_h × 1.85cm
#   width_panel × 2 = (unit_width − 80mm) × body_h × 1.85cm   (bottom slides)
# ============================================================
synth_panels = []
synth_count = 0
for p in panels:
    if not p['suffix'].startswith('DrawerFront'): continue
    x_cm, y_cm, z_cm = p['dims_xyz_cm']
    if not (1.7 < z_cm < 2.0): continue  # must be a real flat front

    front_h_cm = x_cm  # X = vertical height for fronts
    body_h_cm = front_h_cm - 2.0
    if body_h_cm <= 1.0:
        continue

    unit_w_cm = unit_width_cm[p['unit']]
    depth_panel_L = 45.0
    width_panel_L = unit_w_cm - 8.0  # bottom slides

    idx_match = re.search(r'_(\d+)$', p['suffix'])
    idx_str = f"_{idx_match.group(1)}" if idx_match else ""

    # Body panels also have Length = vertical axis. Pick orientation so Length = body_h_cm
    # Encode as [X=body_h, Y=panel_length, Z=thickness] so the builder reads x as height
    depth_xyz   = [body_h_cm, depth_panel_L, 1.85]
    width_xyz   = [body_h_cm, width_panel_L, 1.85]
    depth_sorted = sorted(depth_xyz, reverse=True)
    width_sorted = sorted(width_xyz, reverse=True)

    for letter in ('a', 'b'):
        synth_panels.append({
            'name': f"U{p['unit']}_DrawerBody_Depth{idx_str}_{letter}",
            'unit': p['unit'],
            'suffix': f'DrawerBody_Depth{idx_str}_{letter}',
            'dims_xyz_cm': depth_xyz,
            'dims_sorted_desc': depth_sorted,
        })
        synth_panels.append({
            'name': f"U{p['unit']}_DrawerBody_Width{idx_str}_{letter}",
            'unit': p['unit'],
            'suffix': f'DrawerBody_Width{idx_str}_{letter}',
            'dims_xyz_cm': width_xyz,
            'dims_sorted_desc': width_sorted,
        })
    synth_count += 1

print(f"DrawerFronts found:           {synth_count}")
print(f"Synthesized body panels:      {len(synth_panels)} (4 per drawer)")

all_panels = panels + synth_panels

# ============================================================
# Step 5: Save to ~/Desktop/scene_data.json
# ============================================================
export = {'units': unit_meta, 'panels': all_panels}
out_path = os.path.join(os.path.expanduser('~'), 'Desktop', 'scene_data.json')
with open(out_path, 'w') as f:
    json.dump(export, f, indent=2)

print(f"\n✓ Saved {len(all_panels)} panels and {len(unit_meta)} units")
print(f"  Path: {out_path}")
print(f"  Size: {os.path.getsize(out_path)} bytes")
