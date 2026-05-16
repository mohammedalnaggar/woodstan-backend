# Furniture Manufacturing Cut-List Platform

## Executive Summary & Delivery Phases

---

# 1. Executive Summary

The Furniture Manufacturing Cut-List Platform is a domain-specific manufacturing system designed to convert structured cabinet/unit definitions into production-ready cut lists, hardware bills of materials, and fabrication documentation for woodworking and cabinetry workshops.

The platform is NOT a CAD or 3D modeling tool. Instead, it functions as a deterministic manufacturing engine that transforms parametric furniture definitions into structured, validated, and traceable manufacturing outputs suitable for production, procurement, and CNC workflows.

## Core Objective

To eliminate manual cut list preparation and hardware specification by automating the conversion of cabinet specifications into accurate, validated, standardized manufacturing outputs that a workshop can execute immediately.

## Key Capabilities

- Maintain a **Workshop Profile** — a global settings entity (assembly method, carcass material thickness, back panel thickness, edge banding thickness) that governs manufacturing defaults for every project in the workshop
- Define furniture units using structured parameters (width, height, depth, type, configuration) — all dimensions expressed in **centimetres (cm)**
- Import cabinet definitions from Blender via `json-generator.py` JSON exports
- Generate complete cut lists for all cabinet components with full metadata
- Generate hardware bills of materials (hinges, slides, connectors, fasteners)
- Include manufacturing metadata such as:
  - Material type and thickness
  - Panel dimensions in cm (finished dimensions)
  - Grain direction
  - Edge banding rules (type, thickness, sides)
  - Assembly method (full sides / full top & bottom)
  - Hardware operations (drilling patterns, hinge cup locations, slide mounting)
  - Part labeling and traceability identifiers
- Validate manufacturability before output generation
- Export production-ready outputs (CSV / JSON / future CNC formats / labels)

## System Philosophy

- Structured data is the source of truth (not geometry)
- Manufacturing rules must be deterministic, repeatable, and validated
- Every generated part must be traceable to its origin unit
- The system prioritizes correctness and manufacturability over visualization
- The system must reject unbuildable configurations, not silently produce bad output
- The Workshop Profile is the single source of truth for all global manufacturing defaults — no hardcoded material or assembly constants anywhere in the engine
- Assembly method is a first-class domain concept that drives all panel dimension calculations

## Technology Stack

| Layer | Technology |
|-------|------------|
| Backend API | Python 3.11+ / FastAPI (OpenAPI-first) |
| Database | PostgreSQL — SQLAlchemy ORM + Alembic migrations |
| Frontend | React + Vite — AG Grid or TanStack Table for cut list dashboards |
| Blender Integration | JSON-only via `json-generator.py` → `scene_data.json` (no geometry) |
| Testing | pytest (backend) + Vitest (frontend) |
| Engine Layer | Pure Python modules — no framework dependencies, independently testable |

> Full technology constraints and rationale: `.specify/memory/constitution.md` (v1.0.0).

---

# 2. High-Level Architecture Overview

The system is structured as a pipeline with integrated validation:

```
Input (Unit Definitions + Construction Rules)
    ↓
Schema Validation
    ↓
Construction Method Engine (Joinery Logic)
    ↓
Dimension Calculation Engine
    ↓
Part Generation Engine
    ↓
Manufacturability Validation
    ↓
Cut List Aggregation + Hardware BOM
    ↓
Export Layer (CSV / JSON / Labels)
```

## Core Domain Models

```
WorkshopProfile  ← global, one per workshop installation
├── assembly_method: full_sides | full_top_bottom
├── carcass_material_thickness (cm)
├── back_panel_thickness (cm)
└── edge_banding_thickness (cm)

Project
└── Room / Zone
    └── Unit (Cabinet)
        ├── type: lower | mid-upper | high-upper
        ├── Parameters (W × H × D in cm, configuration)
        ├── Material Assignment (references WorkshopProfile defaults)
        └── Parts[]
            ├── Panel (material, dimensions in cm, grain, edge banding)
            └── Hardware Item (type, quantity, mounting location)
```

**Assembly Methods:**
- **full_sides** — side panels run the full height of the unit, covering the top and bottom panels on both ends. Inner width = W − (2 × carcass_thickness). Inner height = H.
- **full_top_bottom** — top and bottom panels run the full width, covering the side panels. Inner width = W. Inner height = H − (2 × carcass_thickness).

**Lower unit rule:** All lower units use two horizontal stretchers (front and back, each 10cm deep × inner_width wide) in place of a full top panel. Exception: corner units, which have no stretchers.

---

# 3. Delivery Phases

## Phase 0 — Constitution & Domain Foundation ✅ Complete

Defines the system's fundamental principles, domain language, and construction standards.

### Objectives

- Establish manufacturing terminology and ubiquitous language
- Define system boundaries (non-CAD system, validation-first)
- Define architectural principles and immutability rules
- Define core constraints and material assumptions
- Catalog construction methods and their dimensional impact

### Outputs

- **Domain Vocabulary:** WorkshopProfile, Unit, Panel, Part, Material, AssemblyMethod, EdgeBanding, HardwareItem, GrainDirection, ManufacturingOperation
- **Unit Type Catalog:**
  - `lower` — base units below the countertop; may have drawers; use stretchers instead of a top panel (except corner units)
  - `mid-upper` — upper units at mid-height (over countertop, reachable); doors only
  - `high-upper` — upper units at high height (above mid-uppers); doors only
- **Assembly Method Catalog:**
  - `full_sides` — side panels full height, covering top and bottom (sides are outside)
  - `full_top_bottom` — top and bottom panels full width, covering sides (top/bottom are outside)
- **Workshop Profile:** Global settings entity — assembly method, carcass thickness, back panel thickness, edge banding thickness; no hardcoded manufacturing constants in any engine function
- **Dimension Standard:** All cabinet dimensions (W, H, D) are expressed in centimetres (cm)
- **System Principles:** Determinism, traceability, validation-first, immutability of generated parts, dual-input parity
- **High-Level Architecture Rules:** Pipeline stages, pure functions for calculations, separation of generation from presentation

### Acceptance Criteria

A new team member can read the constitution and understand exactly what the system does, what it does not do, and how a base cabinet is defined in domain terms.

**Status: Complete** — Constitution ratified at `.specify/memory/constitution.md` (v1.0.0, 2026-05-16).

---

## Phase 1 — Cabinet Domain Engine (Core Logic + Validation)

Implements the core transformation engine from cabinet definitions to validated parts.

**Scope:** This phase produces a pure Python engine with no HTTP or database dependencies. All calculation and validation functions are pure (stateless, no I/O). The API and persistence layer are introduced in Phase 3. This phase is the prerequisite for all subsequent phases.

### Objectives

- Define the Workshop Profile model — the global settings entity that all dimension calculations must read from; no hardcoded manufacturing constants
- Define unit schemas with strict validation using the unit type vocabulary (lower, mid-upper, high-upper)
- Implement assembly-method-aware dimension calculations — one dedicated resolver per assembly method (full_sides, full_top_bottom)
- Generate complete part sets for all three unit types
- Enforce structural rules: lower units always include front and back stretchers (except corner units)
- Validate manufacturability of all outputs
- Implement deterministic part traceability identifiers

### Unit Types (Initial Support)

- **lower** — base units (with/without drawers, adjustable shelves); uses two stretchers in place of a top panel, except corner units
- **mid-upper** — upper units at mid-height (doors only, no drawers)
- **high-upper** — upper units at high height (doors only, no drawers)

### Outputs

- Workshop Profile model (assembly method + material thicknesses + edge banding thickness)
- Unit data models (immutable parameter sets referencing the Workshop Profile)
- Part generation engine with one assembly method resolver per method (`full_sides`, `full_top_bottom`)
- Dimension calculation engine (reads all thickness values from the Workshop Profile — no hardcoded constants)
- Manufacturability validator (dimensional sanity, material constraints, structural rules)
- Part labeling schema (e.g., `CAB-001-LS-01` = Cabinet 001, Left Side, Part 01)
- pytest test suite: one test per assembly method resolver, one test per validation rule

### Validation Rules (Examples)

- Shelf span must not exceed material-specific maximum (prevents sag)
- Drawer width must account for slide clearance
- Minimum/maximum dimension guards per part type (dimensions in cm)
- Lower units (non-corner) MUST include exactly two stretchers — front (no groove) and back (with groove)
- Corner units MUST NOT include stretchers
- Drawers exist only in lower units — mid-upper and high-upper units reject drawer configuration
- All dimension calculations MUST read thickness values from the Workshop Profile — no hardcoded constants

### Acceptance Criteria

- A lower unit input produces a complete, validated set of parts including two stretchers (front and back) in place of a top panel
- A mid-upper or high-upper unit input produces a complete part set with top and bottom panels but no stretchers and no drawers
- Invalid inputs are rejected with typed error objects listing all violations (rule, offending_value, limit) — zero silent failures
- Part identifiers are deterministic and traceable — identical inputs always produce identical identifiers
- Switching assembly method (full_sides → full_top_bottom) on the Workshop Profile produces correctly different part dimensions for all units
- All dimension resolution functions are pure (no I/O, no side effects, no hardcoded constants) and pass pytest without a running server or database connection
- All cabinet dimensions (W, H, D) are expressed in centimetres (cm)

---

## Phase 2 — Cut List & Hardware BOM Engine

Standardizes generated parts and hardware into manufacturing-ready outputs with full metadata.

**Scope:** This phase remains in the pure engine layer (no HTTP, no database). Outputs are structured data models and export functions that the API layer (Phase 3) will call.

### Objectives

- Normalize part structures for downstream consumption
- Add complete manufacturing metadata to every part
- Generate hardware bill of materials per unit
- Enable grouping, sorting, and aggregation by material, unit, or operation
- Generate machine-ready part labels

### Outputs

- **Structured Cut List Model:**

```json
{
  "id": "CAB-001-LS-01",
  "unitId": "CAB-001",
  "unitType": "Base Cabinet",
  "name": "Left Side Panel",
  "material": "18mm MDF - White",
  "quantity": 1,
  "dimensions": { "width": 560, "height": 720, "thickness": 18 },
  "grainDirection": "vertical",
  "edgeBanding": [
    { "edge": "front", "type": "1mm PVC", "color": "White" },
    { "edge": "top",   "type": "1mm PVC", "color": "White" }
  ],
  "operations": ["line-bore-system-holes", "hinge-cup-35mm"],
  "label": "CAB-001-LS-01 | 560×720 | 18mm MDF White | Edge: Front,Top"
}
```

- **Hardware BOM Model:**

```json
{
  "partId": "HDW-CAB-001-01",
  "unitId": "CAB-001",
  "type": "Blum Clip Top 110°",
  "quantity": 2,
  "mountingPart": "CAB-001-LS-01",
  "notes": "35mm cup, 3mm reveal"
}
```

- CSV/JSON export functions with configurable columns
- Label string generation for part identification on shop floor

### Acceptance Criteria

- A complete base cabinet generates a cut list with all panels and a hardware BOM with all required items and correct quantities
- Exports contain all metadata required for procurement and fabrication
- Identical inputs produce identical export files (determinism requirement)
- Label strings are deterministic and contain all required part identifiers

---

## Phase 3 — Project & Unit Management Layer

Introduces multi-unit and project-level organization, the REST API, and database persistence.

**Persistence boundary:** This is the phase where FastAPI endpoints and PostgreSQL models are introduced. Phases 1 and 2 deliver pure engine logic; Phase 3 wires the engine to the API and database.

### Objectives

- Expose unit and project management via a FastAPI REST API
- Organize units into rooms/zones
- Enable batch processing and project-wide cut list aggregation
- Support unit cloning and variation
- Introduce PostgreSQL persistence (SQLAlchemy models + Alembic migrations)

### Outputs

- **Project Structure:**

```
Project "Smith Kitchen"
├── Room "Kitchen"
│   ├── Unit "CAB-001" (Base Cabinet 600mm)
│   ├── Unit "CAB-002" (Base Cabinet 900mm)
│   └── Unit "CAB-003" (Wall Cabinet 600mm)
└── Room "Pantry"
    └── Unit "CAB-004" (Tall Cabinet 600mm)
```

- FastAPI REST endpoints: Project CRUD, Room CRUD, Unit CRUD (with clone + variation)
- PostgreSQL schema and Alembic migrations for: projects, rooms, units, generated part snapshots
- Project-wide aggregated cut list (all parts across all units, sorted by material)
- Project-wide hardware BOM (all hardware across all units, sorted by type)
- Material requirements summary (estimated sheet counts, edge banding totals)

### Acceptance Criteria

- A project with multiple units across rooms generates a single aggregated cut list via API
- Material requirements are summarized by type with estimated sheet counts
- Cloning a unit and changing one parameter produces a new unit whose parts differ only in dimensions affected by that parameter
- All API responses include full traceable part identifiers
- Database migrations are reversible

---

## Phase 4 — Frontend Operational Dashboards

Provides UI for interacting with the system. Spreadsheet-like, not CAD-like.

**Tech:** React + Vite. AG Grid or TanStack Table for cut list views. All dimension calculations remain in the backend — the frontend is display and input only.

### Objectives

- Build operational dashboards for production workflow
- Enable fast unit definition and parameter editing
- Provide cut list and hardware review with filtering
- Show validation errors inline before generation

### Screens

- **Projects Dashboard**
  - Project list with status
  - Project-level material summaries
  - Quick actions (new project, import from Blender)

- **Unit Builder Dashboard**
  - Parameter form (W×H×D, configuration, construction method, materials)
  - Real-time validation feedback (errors displayed before generation is triggered)
  - Part preview (list view, not 3D/visual)
  - Clone and variation controls

- **Cut List Dashboard**
  - Sortable/filterable table (by material, unit, operation)
  - Hardware BOM view
  - Export controls (CSV, JSON)
  - Label print queue

- **Materials & Rules Dashboard**
  - Material library (thickness, type, cost, supplier)
  - Edge banding library
  - Hardware library
  - Construction method configurations

### Acceptance Criteria

- A user can define a base cabinet, see real-time validation, view the generated parts list, and export a CSV without leaving the application
- Filtering by material shows only parts for that material across all units in the project
- The frontend performs no dimension calculations — all values are received from the API

---

## Phase 5 — Blender Integration Layer

Enables import of structured cabinet definitions from Blender via `json-generator.py`.

**Parallel execution:** This phase can begin once Phase 1 is complete and run in parallel with Phases 2–4.

### Objectives

- Accept `scene_data.json` exports produced by `json-generator.py` (Blender Cabinet Designer workflow)
- Validate imported cabinet definitions against the same schemas and validators used for UI-created units
- Map Blender semantic data to the internal unit schema
- Preserve material and parameter assignments from the Blender scene

### Constraints

- No geometry parsing — no mesh analysis, no STL/OBJ processing
- Only semantic/parametric data import
- The backend MUST NOT depend on Blender's Python API (`bpy`) or any mesh library
- The same validator used for UI-created units MUST be used for imported units — no special-casing of the import path

### Data Mapping

| Blender Export (`scene_data.json`) | Internal Schema |
|------------------------------------|-----------------|
| Cabinet parameters (W, H, D) | `Unit.parameters` |
| Material assignments | `Unit.materialAssignment` |
| Shelf/drawer configuration | `Unit.configuration` |
| Label/metadata | `Unit.metadata` |

### Acceptance Criteria

- A valid Blender JSON export passes through the same validation and dimension resolution pipeline as a UI-defined unit with equivalent parameters, producing identical cut list parts — verified by automated dual-input parity tests
- Invalid Blender exports are rejected with the same error format as UI validation failures
- The import endpoint rejects any payload that includes raw geometry or mesh data

---

## Phase 6 — Rules Configuration System

Externalizes manufacturing logic into configurable, editable rules.

**Parallel execution:** This phase can begin once Phase 1 is complete and run in parallel with Phases 2–4.

### Objectives

- Define material rules (thickness, availability, cost, supplier)
- Define cabinet construction rules (joinery defaults, clearances, tolerances)
- Define hardware rules (hinge selection by door type, slide selection by drawer depth)
- Define edge banding rules (auto-apply based on material and edge visibility)
- Support rule versioning for different manufacturing standards

### Rule Examples

```
Rule: "Base Cabinet Side Panel — Dowel Construction"
When: unit.type == "base" AND construction == "dowel"
Then:
  sidePanel.depth  = unit.depth - backPanel.thickness
  sidePanel.height = unit.height - toekick.height - countertop.thickness
  sidePanel.systemHoles = true
  sidePanel.systemHoleStart = 37mm from bottom (32mm system)

Rule: "Hinge Selection — Full Overlay MDF Door"
When: door.overlay == "full" AND door.material == "18mm MDF"
Then:
  hinge.type         = "Blum Clip Top 110°"
  hinge.boreDistance = 5mm
  hinge.quantity     = door.height > 1200mm ? 4 : 3
```

### Outputs

- Configurable rule engine with versioned rule sets
- Editable manufacturing standards (stored in PostgreSQL, editable via API/UI)
- Rule import/export for sharing standards between projects
- Rule override capability at unit level

### Acceptance Criteria

- Changing a construction method rule updates part dimensions for all affected cabinets in the project
- Rule sets can be exported and imported between projects
- Rule version changes are auditable (prior rule versions retained alongside new ones)

---

## Phase 7 — Costing & Quotation Engine

Introduces business-level outputs for pricing and estimation.

### Objectives

- Material cost estimation from cut lists (panel area × cost per sheet)
- Hardware cost calculation from BOM (quantity × unit cost)
- Labor estimation based on operation count per part (cost per drill operation, per cut, per bore)
- Profit margin and markup calculation
- Quotation document generation

### Costing Model

```
Cabinet Cost =
  SUM(part.area × material.costPerSheet / sheet.area)   -- material
  + SUM(hardware.quantity × hardware.unitCost)           -- hardware
  + SUM(part.operationCount × operation.laborRate)       -- labor
  + (subtotal × overheadPercentage)
  + (subtotal × marginPercentage)
```

### Outputs

- Quotation reports (per unit and per project)
- Cost breakdowns by category (material / hardware / labor / overhead / margin)
- Material procurement list with line-item costs
- Hardware procurement list with line-item costs

### Acceptance Criteria

- A complete kitchen project generates a priced quotation with line-item detail per unit and per part
- Cost changes propagate automatically when material or hardware selections change
- Quotation reflects the current state of the cut list — no stale cost data

---

## Phase 8 — Optimization Engine (Future Phase)

Implements sheet material optimization and nesting logic.

### Objectives

- Optimize panel layout on standard sheet sizes to minimize material waste
- Respect grain direction constraints during optimization
- Generate sheet layout maps
- Support multiple sheet sizes and materials simultaneously

### Architectural Considerations

- Requires fundamentally different data structures (geometric placement coordinates vs. part parameter lists)
- Must integrate with the existing part metadata model without breaking Phases 1–7
- May require external nesting libraries
- Grain direction constraints significantly impact optimization algorithms
- **Do not design Phases 1–7 around optimization requirements** — this phase adapts to the existing schema

### Outputs

- Optimized cut layouts per sheet
- Sheet utilization reports with waste percentage
- Cut sequence suggestions

---

# 4. Key Architectural Principles

These principles are codified in `.specify/memory/constitution.md` (v1.0.0). The list below is a quick reference — the constitution is the authoritative source.

- **Structured data is the system of record** — No geometry parsing, no mesh dependence
- **All outputs must be deterministic** — Same input always produces identical parts (pure functions)
- **Manufacturing constraints are first-class logic** — Validation rejects unbuildable designs at definition time, not on the shop floor
- **Construction methods drive dimensions** — One resolver per method; no single universal formula
- **Every part is traceable** — Deterministic identifiers (e.g., `CAB-001-LS-01`) link every output to its origin project, unit, and role
- **Immutability of generated outputs** — Generated parts are versioned snapshots, not mutable records
- **Dual-input parity** — UI-defined and Blender-imported units share identical schemas, validators, and resolvers
- **System must remain extensible** — CNC post-processor integration, inventory systems, supplier APIs reserved for future phases
- **Validation is proactive** — Reject at definition time, not after generation

---

# 5. Long-Term Vision

The platform evolves into a full manufacturing intelligence system covering:

- **CNC Integration:** Direct post-processor output (WoodWOP, Xilog, etc.)
- **Production Tracking:** Part status from cut to assembly to installation
- **Inventory Management:** Material stock tracking and reorder triggers
- **Supplier Integration:** Automated material and hardware ordering
- **Shop Floor Interface:** Tablet-based part tracking and assembly instructions
- **Version Control:** Project and unit revision history
- **Multi-Facility:** Support for multiple manufacturing locations with different capabilities

---

# 6. Phase Summary & Dependencies

```
Phase 0: Constitution         ← No dependencies                    ✅ Complete
Phase 1: Domain Engine        ← Phase 0
Phase 2: Cut List + BOM       ← Phase 1
Phase 3: Project Management   ← Phase 2                (introduces API + DB)
Phase 4: Frontend UI          ← Phase 3
Phase 5: Blender Integration  ← Phase 1  ‖ parallel with Phases 2–4
Phase 6: Rules Config         ← Phase 1  ‖ parallel with Phases 2–4
Phase 7: Costing              ← Phase 2, Phase 6
Phase 8: Optimization         ← Phase 2  (future — architectural consideration only)
```

**Persistence boundary:** Phases 1 and 2 are pure engine layers (no HTTP, no database). Phase 3 introduces FastAPI endpoints and the PostgreSQL schema.
