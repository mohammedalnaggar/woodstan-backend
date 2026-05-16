<!--
SYNC IMPACT REPORT
==================
Generated: 2026-05-16
Constitution Version: 1.0.0

Version change: N/A (initial fill) → 1.0.0 (MAJOR — initial ratification)
Principles added: All 7 (initial ratification)
Principles removed: None
Sections added: Core Principles, Technology Stack and Integration Constraints,
  Development Workflow, Governance
Templates requiring updates:
  - .specify/templates/plan-template.md ✅ Constitution Check section updated
  - .specify/templates/spec-template.md ✅ No changes needed
  - .specify/templates/tasks-template.md ✅ No changes needed
Deferred TODOs: None
Skills reference docs (not modified):
  - skills/cabinet-specs/SKILL.md — workshop construction standards (reference only)
  - skills/cutlist/SKILL.md — cut list generation workflow (reference only)
-->

# Woodstan Cut-List Platform Constitution

## Core Principles

### I. Structured Data Is the System of Record (NON-NEGOTIABLE)

The system MUST derive all manufacturing outputs exclusively from structured,
parametric cabinet definitions. The system MUST NOT parse geometry, meshes,
STL/OBJ files, or any 3D coordinate data to produce outputs. All data models
MUST be expressible as typed records with scalar fields (dimensions,
enumerations, identifiers, material references). Any integration that supplies
input data — including Blender exports via `json-generator.py` — MUST produce
semantic JSON conforming to the internal unit schema before being processed by
any engine layer; raw mesh data MUST be discarded at the integration boundary.

### II. All Outputs Must Be Deterministic

Given identical input parameters (unit definitions, material assignments,
construction method, rules configuration), the system MUST produce identical
cut list parts, hardware BOM entries, and fabrication metadata across every
invocation, on every machine, at any point in time. Non-determinism in part
dimensions, identifiers, ordering, or quantity MUST be treated as a defect.
Engine functions that compute dimensions or generate parts MUST be pure
functions with no hidden state, random seeds, or timestamp-dependent logic.

### III. Manufacturing Constraints Are First-Class Validation Logic

The system MUST validate the manufacturability of every cabinet definition
before generating any output. Unbuildable configurations — shelf spans
exceeding material-specific sag limits, widths that cannot accommodate the
selected joinery method, drawer dimensions that violate slide clearance rules,
and any dimension outside defined min/max guards — MUST be rejected with
specific, actionable error messages at definition time. The system MUST NOT
silently generate outputs for invalid inputs or defer validation to a
downstream step. Validation MUST occur before any part generation engine runs.

### IV. Construction Methods Drive Dimension Resolution

Every supported construction method — butt joint with confirmat screws, dowel
(32mm system), domino/loose tenon, rabbet/dado, and blind dado — MUST have its
own dedicated dimension resolver that accounts for the method's exact material
overlap, joinery depth, clearance, and component relationship rules. The system
MUST NOT use a single universal dimension formula across all methods. Changing
a unit's construction method MUST produce demonstrably different finished part
dimensions. Adding a new construction method MUST require implementing a new
resolver, not modifying shared calculation logic.

### V. Every Part Is Fully Traceable to Its Origin

Every generated part — panel, hardware item, synthesized drawer body, or
aggregated material entry — MUST carry a deterministic identifier that encodes
its origin project, unit, and component role (e.g., `CAB-001-LS-01` = Cabinet
001, Left Side, Part 01). Identifiers MUST be stable: identical input parameters
MUST always produce identical identifiers. The system MUST NOT generate anonymous
parts or positional references. Every API response, export file, and label MUST
include the full traceable identifier.

### VI. Generated Outputs Are Immutable and Versioned

Once a set of parts has been generated for a unit, those parts MUST be treated
as an immutable snapshot. The system MUST NOT mutate a previously generated
part record in place. Parameter changes MUST produce a new generation snapshot,
preserving prior snapshots for audit. Export files MUST include a generation
timestamp and a hash/version that links the export to its exact input
parameters. Regenerating from identical inputs MUST produce an identical
snapshot.

### VII. Dual-Input Parity: UI and Blender Import Are Equivalent Paths

A unit defined manually through the UI and a unit imported from a Blender JSON
export (via `json-generator.py`) MUST resolve to the same internal schema and
MUST produce identical manufacturing outputs when their parameters are
equivalent. The system MUST NOT implement separate generation logic, separate
validation rules, or separate dimension resolvers for UI-created vs. imported
units. The Blender import path MUST include full schema validation and
manufacturability validation using the same validator that processes UI-defined
units. Parity MUST be verified by automated tests.

---

## Technology Stack and Integration Constraints

**Backend**: Python 3.11+ / FastAPI. Domain engine logic MUST be implemented
as pure Python functions with no framework dependencies, enabling independent
unit testing. SQLAlchemy (with Alembic for migrations) MUST be used for all
database access; raw SQL MUST NOT appear in application logic. PostgreSQL is
the only supported database engine.

**Frontend**: React + Vite. Dashboards are spreadsheet-like (sortable tables,
parameter forms, export controls) — NOT visual or CAD-like interfaces. AG Grid
or TanStack Table MUST be used for cut list views; custom grid implementations
are prohibited. The frontend MUST NOT perform any dimension calculation or
manufacturing logic; all computation MUST reside in the backend engine layer.

**Blender Integration Boundary**: The integration is limited to
`json-generator.py`, which runs inside Blender and produces `scene_data.json`.
The backend MUST receive only this JSON file at the API boundary. The backend
MUST NOT depend on Blender's Python API (`bpy`), mesh libraries, or any geometry
toolkit. The `scene_data.json` schema is the contract; changes require a
version bump and migration of import endpoints.

**Engine Layer Isolation**: The dimension calculation engine, part generation
engine, and manufacturability validator MUST be implemented as pure, stateless
Python modules with no FastAPI, SQLAlchemy, or HTTP dependencies. These modules
MUST be independently importable and testable via pytest without starting a
server or connecting to a database.

**Testing**: pytest is REQUIRED for all backend tests. The test suite MUST
include unit tests for every dimension resolver (one per construction method),
unit tests for every validation rule, and integration tests verifying dual-input
parity (Principle VII). Frontend tests MUST use Vitest or a compatible React
testing library.

**Export Formats**: CSV and JSON are the only supported export formats for
Phases 1–3. CNC-specific formats (WoodWOP, Xilog) are reserved for future
phases and MUST NOT be introduced into the core engine prematurely.

**No Geometry Dependencies**: The system MUST NOT introduce any library that
performs geometric computation, mesh processing, or spatial indexing (e.g.,
Shapely, Open3D, trimesh). numpy MAY be used strictly for numeric utilities
with explicit justification.

**Reference Documentation**: `skills/cabinet-specs/SKILL.md` (workshop
construction standards) and `skills/cutlist/SKILL.md` (cut list generation
workflow) serve as authoritative domain reference. They are NOT application
code and MUST NOT be modified as part of feature implementation.

---

## Development Workflow

**Validation Before Generation**: Any feature adding a new cabinet type,
construction method, or material rule MUST implement the manufacturability
validator before implementing the generation logic. A feature MUST NOT merge if
its generation path can produce parts without passing validation.

**Pure Function First**: Every new dimension resolver, part generator, or BOM
calculator MUST be implemented as a pure function with a typed signature and
passing unit tests before being integrated into any API endpoint.

**Phase Order**: Deliver in dependency order per `PLAN.MD`. Phase N MUST be
complete before Phase N+1 begins, except where `PLAN.MD` explicitly marks
parallel paths (Phases 5 and 6 can run in parallel with Phases 2–4).

**Schema Change Protocol**: Any change to the internal unit schema or
`scene_data.json` MUST be accompanied by an Alembic migration, a schema version
bump, and updated dual-input parity tests. Schema changes MUST NOT merge without
passing parity tests.

**Pull Request Checklist**: Every PR MUST confirm:
- All 7 constitution principles are satisfied, or a Complexity Tracking entry
  justifies any deviation
- No geometry library introduced as a dependency
- All new engine functions are pure and independently tested
- Dual-input parity test passes if the change touches unit schema or import logic

---

## Governance

This constitution supersedes all other development practices for the Woodstan
Cut-List Platform. `PLAN.MD` defines the authoritative delivery roadmap; phase
objectives and acceptance criteria in `PLAN.MD` are binding.

**Amendment Process**: Amendments MUST (1) identify the affected principle and
rationale, (2) increment the version per semantic versioning, (3) update the
Sync Impact Report at the top of this file, and (4) propagate changes to
dependent templates. Amendments MUST be reviewed before any feature that depends
on the new wording begins implementation.

**Complexity Justification**: Any deviation from a principle MUST be entered in
the Complexity Tracking table of the relevant plan with an explanation of why
the deviation is necessary and why a compliant alternative was insufficient.

**Version History**:

| Version | Date       | Change Summary                     |
|---------|------------|------------------------------------|
| 1.0.0   | 2026-05-16 | Initial ratification, 7 principles |

**Version**: 1.0.0 | **Ratified**: 2026-05-16 | **Last Amended**: 2026-05-16
