# Quickstart: Cabinet Domain Engine

**Branch**: `001-cabinet-domain-engine` | **Date**: 2026-05-16

---

## What This Phase Delivers

A pure Python engine (`engine/`) that accepts a Workshop Profile + unit definition and returns either a complete set of manufacturing parts or a list of all validation errors. No HTTP server, no database — runs entirely in-process and in pytest.

---

## Directory Structure

```
engine/
├── __init__.py            ← public entry point: generate_unit()
├── models/
│   ├── profile.py         ← WorkshopProfile, AssemblyMethod
│   ├── unit.py            ← UnitDefinition, UnitType, DrawerConfig
│   ├── part.py            ← Part, PartRole, EdgeBanding
│   ├── room.py            ← RoomContext
│   ├── result.py          ← GeneratedUnit, DimensionSet
│   └── errors.py          ← ValidationError + rule name constants
├── resolvers/
│   ├── base.py            ← dispatches to full_sides or full_top_bottom
│   ├── full_sides.py      ← dimension resolver for full_sides assembly
│   └── full_top_bottom.py ← dimension resolver for full_top_bottom assembly
├── generators/
│   ├── base.py            ← generate_parts() + assign_unit_id()
│   ├── lower.py           ← lower unit structural panels + stretchers
│   ├── upper.py           ← upper unit structural panels
│   ├── shelves.py         ← shelf generation (shared)
│   └── drawers.py         ← drawer box parts
└── validators/
    ├── runner.py           ← collect-all validation runner
    └── rules.py            ← one function per named rule

tests/
├── conftest.py             ← shared fixtures (default profile, sample units)
├── resolvers/
│   ├── test_full_sides.py
│   └── test_full_top_bottom.py
├── generators/
│   ├── test_lower_unit.py
│   ├── test_upper_unit.py
│   └── test_drawers.py
└── validators/
    └── test_rules.py
```

---

## Implementation Order

Build in this order — each step is independently testable before the next begins:

1. **Models** — all dataclasses (`WorkshopProfile`, `UnitDefinition`, `Part`, `ValidationError`, etc.). No logic, just typed data structures with `frozen=True`.

2. **Resolvers** — `resolve_dimensions()` for each assembly method. Write tests first. These are pure math functions; no validation required.

3. **Validators** — one function per rule in `rules.py`. Wire into `runner.py`. Test each rule individually with the exact `rule`, `offending_value`, and `limit` values the contract defines.

4. **Generators** — `generate_parts()` per unit type. Use the dimensions from the resolvers. Test completeness of the returned part list per unit type (see Part Generation Matrix in data-model.md).

5. **Entry point** — `generate_unit()` in `engine/__init__.py`. Composes: resolve → validate → (if clean) generate → return. Test the full round-trip.

---

## Key Invariants to Verify in Tests

- `generate_unit()` never returns both a `GeneratedUnit` and a list of errors.
- Running the same inputs 10× always produces the same output (determinism test).
- Lower non-corner units always have exactly two stretchers (STF-01, STB-01).
- Corner lower units have zero stretchers.
- Mid-upper and high-upper units have a top panel and no stretchers.
- All part dimensions are in cm; no millimetre values appear in any Part field.
- Every rule is exercised by at least one test that asserts on `rule`, `offending_value`, and `limit` individually.

---

## Running Tests

```bash
# From repo root
pytest tests/ -v

# Run a specific resolver test
pytest tests/resolvers/test_full_sides.py -v

# Run all validation rule tests
pytest tests/validators/test_rules.py -v
```

No server, no database, no environment variables required. Cold-start to all tests passing in under 60 seconds.

---

## Default Workshop Profile (for tests)

```python
# tests/conftest.py
import pytest
from engine.models.profile import WorkshopProfile, AssemblyMethod

@pytest.fixture
def default_profile():
    return WorkshopProfile(
        assembly_method=AssemblyMethod.full_sides,
        carcass_thickness=1.855,
        back_panel_thickness=0.7,
        edge_banding_thickness=0.1,
    )

@pytest.fixture
def full_top_bottom_profile():
    return WorkshopProfile(
        assembly_method=AssemblyMethod.full_top_bottom,
        carcass_thickness=1.855,
        back_panel_thickness=0.7,
        edge_banding_thickness=0.1,
    )
```
