# Implementation Plan: Cabinet Domain Engine

**Branch**: `001-cabinet-domain-engine` | **Date**: 2026-05-16 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-cabinet-domain-engine/spec.md`

## Summary

Implement a pure Python engine that accepts a Workshop Profile (global assembly settings), a unit definition (lower / mid-upper / high-upper), and a room context, then returns either a complete, labelled set of manufacturing parts or a collect-all list of typed validation errors. No HTTP, no database. All dimensions in cm. The engine's two assembly method resolvers (`full_sides`, `full_top_bottom`) read all material thickness values from the Workshop Profile — no hardcoded constants anywhere in the codebase.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: Standard library only for the engine (`dataclasses`, `enum`). `pytest` for testing. No FastAPI, no SQLAlchemy, no third-party libraries in the engine layer.

**Storage**: N/A — Phase 1 is a pure in-process library. No persistence.

**Testing**: pytest. One test per assembly method resolver. One test per validation rule. Full-suite target: under 60 seconds, no server or database required.

**Target Platform**: Python library (cross-platform). Importable by Phase 3 FastAPI layer without modification.

**Project Type**: library

**Performance Goals**: Test suite completes in under 60 seconds (SC-005). Individual engine calls are synchronous pure functions with no I/O — sub-millisecond is expected and not explicitly tested.

**Constraints**: No external I/O. No side effects. No mutable global state. All functions must be independently importable and testable with `import engine`.

**Scale/Scope**: Single workshop installation. Engine handles one unit definition per call. Batch processing is introduced in Phase 3.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*
*Any failing gate requires a justified entry in the Complexity Tracking table.*

| # | Principle Gate | Status | Notes |
|---|----------------|--------|-------|
| I | Structured Data Is the System of Record — No geometry parsing; all inputs are typed parametric records; Blender import discards mesh data at the boundary | PASS | Phase 1 has no Blender import (that is Phase 5). All inputs are typed dataclasses. |
| II | All Outputs Must Be Deterministic — Engine functions are pure; no hidden state, randomness, or timestamps in output generation | PASS | All engine functions are pure (`frozen=True` dataclasses as input). Room context supplies the sequence seed deterministically. |
| III | Manufacturing Constraints Are First-Class Validation — Validation runs before generation; invalid inputs rejected with specific errors; no silent bad output | PASS | `validate_unit()` runs all rules before `generate_parts()` is called. Collect-all mode. Typed error objects with `rule`, `offending_value`, `limit`. |
| IV | Assembly Method Drives Dimension Resolution — Each method has its own resolver; no universal formula; changing method produces different dimensions | PASS | `full_sides.py` and `full_top_bottom.py` are separate resolvers. `resolve_dimensions()` dispatches based on `profile.assembly_method`. No shared formula. |
| V | Every Part Is Fully Traceable — All parts carry deterministic identifiers encoding project+unit+role; no anonymous parts in any output | PASS | Every Part carries `id = f"{unit_id}-{role}-{seq:02d}"`. Stable abbreviation table in research.md. |
| VI | Generated Outputs Are Immutable and Versioned — No in-place mutation of generated parts; parameter changes produce new snapshots; exports include version/hash | PASS | All models use `frozen=True`. No update/patch operations in Phase 1. Export versioning is introduced in Phase 2. |
| VII | Dual-Input Parity — UI-defined and Blender-imported units share identical schema, validators, resolvers, and generation logic; parity tests exist | N/A | Blender integration is Phase 5. The engine's `UnitDefinition` schema is designed to be the single schema both paths will use. Parity tests are Phase 5 deliverables. |

**Pre-Phase-0 Gate Result:** [x] All gates PASS or N/A (Principle VII deferred to Phase 5 by design)
**Post-Phase-1 Re-check Result:** [x] No design decisions introduced violations. Module layout preserves pure function isolation. N/A gates unchanged.

## Project Structure

### Documentation (this feature)

```text
specs/001-cabinet-domain-engine/
├── plan.md              ← this file
├── research.md          ← Phase 0 output (dimension formulas, sag limits, label codes)
├── data-model.md        ← Phase 1 output (all entities, enums, validation rule table)
├── quickstart.md        ← Phase 1 output (directory layout, build order, test fixtures)
├── contracts/
│   └── engine_api.md    ← Phase 1 output (public function signatures, usage example)
└── tasks.md             ← Phase 2 output (/speckit-tasks — not yet created)
```

### Source Code (repository root)

```text
engine/
├── __init__.py                  ← public entry: generate_unit()
├── models/
│   ├── __init__.py
│   ├── profile.py               ← WorkshopProfile, AssemblyMethod
│   ├── unit.py                  ← UnitDefinition, UnitType, DrawerConfig, DrawerSlideType
│   ├── part.py                  ← Part, PartRole, EdgeBanding
│   ├── room.py                  ← RoomContext
│   ├── result.py                ← GeneratedUnit, DimensionSet
│   └── errors.py                ← ValidationError + RULE_* constants
├── resolvers/
│   ├── __init__.py
│   ├── base.py                  ← resolve_dimensions() dispatcher
│   ├── full_sides.py            ← full_sides resolver
│   └── full_top_bottom.py       ← full_top_bottom resolver
├── generators/
│   ├── __init__.py
│   ├── base.py                  ← generate_parts() + assign_unit_id()
│   ├── lower.py                 ← lower unit: sides, bottom, stretchers, back
│   ├── upper.py                 ← upper units: sides, top, bottom, back
│   ├── shelves.py               ← shared shelf generation
│   └── drawers.py               ← drawer box generation
└── validators/
    ├── __init__.py
    ├── runner.py                 ← validate_unit() collect-all runner
    └── rules.py                  ← one function per named rule

tests/
├── conftest.py                   ← shared fixtures (default_profile, full_top_bottom_profile)
├── resolvers/
│   ├── test_full_sides.py        ← dimensions correct for full_sides assembly
│   └── test_full_top_bottom.py   ← dimensions correct for full_top_bottom assembly
├── generators/
│   ├── test_lower_unit.py        ← part completeness: stretchers, no top panel
│   ├── test_upper_unit.py        ← part completeness: top panel, no stretchers, no drawers
│   └── test_drawers.py           ← drawer box dimensions per slide type
└── validators/
    └── test_rules.py             ← one test per rule; asserts rule/offending_value/limit
```

**Structure Decision**: Single-project Python library layout. No `src/` wrapper — Phase 3 will import `engine` directly as a sibling package inside the FastAPI project. `tests/` mirrors `engine/` module structure for navigability.

## Complexity Tracking

> No constitution violations. No entries required.
