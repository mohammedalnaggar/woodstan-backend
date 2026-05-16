# Feature Specification: Cabinet Domain Engine

**Feature Branch**: `001-cabinet-domain-engine`

**Created**: 2026-05-16

**Status**: Draft

**Input**: User description: "Phase 1 — Cabinet Domain Engine (Core Logic + Validation)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Define and Validate a Lower Unit (Priority: P1)

A workshop engineer defines a lower unit by providing its key parameters (width, height, depth in cm, unit type, and configuration). The engine reads the active Workshop Profile for material thicknesses and assembly method, validates the definition against manufacturing rules, and produces a complete, labelled part set — including two stretchers in place of a top panel.

**Why this priority**: This is the foundational capability — every downstream phase (cut lists, BOM, API, UI) depends on the ability to define a unit and receive valid parts. Without this, nothing else can be built or tested.

**Independent Test**: Can be fully tested by providing a lower unit definition and a Workshop Profile as structured input and asserting that the returned part set contains all expected panels (including front and back stretchers) with correct dimensions in cm and deterministic identifiers — requires no running server or database.

**Acceptance Scenarios**:

1. **Given** a Workshop Profile with assembly method `full_sides`, carcass thickness 1.855cm, back panel thickness 0.7cm, and **Given** a lower unit (W=60cm, H=72cm, D=56cm, no drawers, one shelf), **When** the engine is invoked, **Then** a complete part set is returned including left side, right side, bottom panel, back panel, front stretcher, back stretcher, and shelf — with correct finished dimensions in cm and deterministic labels.
2. **Given** the same inputs submitted twice, **When** the engine runs both times, **Then** the part identifiers and dimensions are identical (determinism requirement).
3. **Given** a lower unit definition with a shelf span that exceeds the maximum allowable for the material, **When** the engine is invoked, **Then** a list of typed error objects is returned — no parts are generated.
4. **Given** a lower unit definition with drawers enabled, **When** the engine is invoked, **Then** drawer box parts are included with widths that account for the required slide clearance per the drawer slide type.

---

### User Story 2 - Resolve Dimensions by Assembly Method (Priority: P2)

A workshop changes its assembly method from `full_sides` to `full_top_bottom` in the Workshop Profile. The engine applies the correct dimensional resolver for the active method and produces parts whose finished dimensions differ appropriately — side panels become shorter; top and bottom panels become wider.

**Why this priority**: Assembly method is a first-class domain concept. Every panel dimension depends on which method is active. This must be verified for both methods before any output can be trusted.

**Independent Test**: Can be fully tested by running the same unit definition against two Workshop Profiles that differ only in assembly method, and asserting that the resulting part dimensions differ in precisely the ways each method dictates.

**Acceptance Scenarios**:

1. **Given** a mid-upper unit with a `full_sides` Workshop Profile, **When** the assembly method is switched to `full_top_bottom` on the profile and the engine is re-run, **Then** the side panel heights decrease and the top and bottom panel widths increase by the exact amount the method dictates.
2. **Given** a Workshop Profile with `full_sides` assembly, **When** any unit is processed, **Then** inner width = W − (2 × carcass_thickness) and the sides run the full height H.
3. **Given** a Workshop Profile with `full_top_bottom` assembly, **When** any unit is processed, **Then** inner height = H − (2 × carcass_thickness) and the top and bottom panels run the full width W.

---

### User Story 3 - Assign Deterministic Part Labels (Priority: P3)

Every generated part carries a deterministic traceability identifier that encodes its unit of origin, its role within that unit, and its sequence number. These identifiers are stable — re-running the engine on the same input always produces the same identifiers.

**Why this priority**: Traceability is a core system principle. Labels must be correct before cut lists or shop floor documents can be generated in later phases.

**Independent Test**: Can be fully tested by comparing the identifiers on parts generated from two identical inputs and asserting they match — and by confirming the label format encodes the expected semantic components (unit ID, part role, sequence).

**Acceptance Scenarios**:

1. **Given** a lower unit whose engine-assigned ID is `CAB-001`, **When** the engine generates the left side panel, **Then** the part identifier is `CAB-001-LS-01`.
2. **Given** the same input run a second time, **When** identifiers are compared, **Then** every identifier is identical to the first run.
3. **Given** a unit with two adjustable shelves, **When** parts are generated, **Then** shelves are labelled sequentially (`CAB-001-SH-01`, `CAB-001-SH-02`) with no gaps or duplicates.
4. **Given** a lower unit, **When** parts are generated, **Then** the front stretcher is labelled `CAB-001-STF-01` and the back stretcher `CAB-001-STB-01`.

---

### User Story 4 - Validate Manufacturability Before Output (Priority: P2)

Before any parts are returned, the engine runs a full manufacturability validation pass across all rules. Any definition that violates one or more rules is rejected with a complete list of typed error objects — the system never silently produces bad output and never truncates the error list.

**Why this priority**: Validation-first is a core system principle. Silent or partial generation of invalid parts would propagate errors downstream to the workshop floor.

**Independent Test**: Can be fully tested by submitting intentionally invalid definitions (one per rule) and asserting that each returns the correct set of typed error objects with the expected `rule`, `offending_value`, and `limit` values.

**Acceptance Scenarios**:

1. **Given** a unit with a shelf whose span (in cm) exceeds the maximum for the material, **When** the engine validates the definition, **Then** a typed error object is returned with `rule="shelf_span_exceeded"`, the submitted span as `offending_value`, and the material's maximum as `limit`.
2. **Given** a mid-upper unit definition that includes a drawer configuration, **Then** validation returns an error with `rule="drawers_not_permitted"` — drawers are only valid in lower units.
3. **Given** a drawer box definition where the drawer width does not account for the required slide clearance, **Then** validation returns an error citing the slide type, required clearance, and actual clearance.
4. **Given** a definition with multiple simultaneous violations, **Then** the engine returns one typed error object per violation — all violations found before any parts are generated.

---

### Edge Cases

- What happens when a lower unit is defined with zero shelves and no drawers? (Valid — open lower unit; engine must generate sides, bottom, back, and two stretchers only.)
- What happens when a lower unit is a corner unit? (Corner units are exempt from the stretcher rule — no stretchers generated; this must be asserted in a dedicated test.)
- What happens when a mid-upper or high-upper unit is a corner unit? (Valid — corner flag applies to all unit types. Carcass generation is the same as a non-corner upper unit in Phase 1. Door widths must be explicitly specified via face_width_L and face_width_R rather than derived from total width; this is enforced in Phase 2 when door generation is introduced.)
- What happens when the Workshop Profile changes between two calls? (Engine is stateless — it reads the profile passed in at call time; no cached state from prior calls.)
- What happens when unit width is exactly the minimum allowable? (Must be accepted as valid — boundary value must not be rejected.)
- What happens when the same unit definition is processed concurrently by multiple callers? (Pure stateless functions — identical results regardless of concurrency.)
- What happens when a high-upper unit is defined with drawer configuration? (Must be rejected — drawers are only valid in lower units.)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST accept three inputs: (1) a Workshop Profile, (2) a structured unit definition, and (3) a room context containing the ordered list of Unit IDs already assigned within the same room. It MUST return either a validated part set (with a newly assigned Unit ID) or a non-empty list of typed validation error objects — never both and never silent failure. Each error object MUST carry: `rule` (constraint name), `offending_value` (the failing value in cm), and `limit` (the allowed threshold in cm). The engine MUST evaluate all validation rules before returning, collecting every violation.
- **FR-002**: The engine MUST support three unit types: `lower`, `mid-upper`, and `high-upper`. No other type identifiers are valid.
- **FR-003**: The engine MUST implement one dedicated dimension resolver per assembly method: `full_sides` (sides cover top and bottom) and `full_top_bottom` (top and bottom cover sides). Every dimension calculation MUST read material thickness values from the Workshop Profile — no hardcoded thickness constants are permitted anywhere in the engine.
- **FR-004**: Every dimension calculation function MUST be a pure function with no I/O, no side effects, and no dependency on a running server or database.
- **FR-005**: The engine MUST generate a complete part set per unit type:
  - **lower units**: left side, right side, bottom panel, front stretcher, back stretcher, back panel, and any configured shelves or drawer boxes. No top panel.
  - **mid-upper / high-upper units**: left side, right side, top panel, bottom panel, back panel, and any configured shelves.
  - Nailers and site-fitted installation strips are out of scope for this phase.
- **FR-006**: The engine MUST generate front and back stretchers for every lower unit, EXCEPT corner units. Corner units MUST NOT include stretchers. This rule is enforced by the validator, not left to the caller.
- **FR-007**: The engine MUST reject drawer configurations on mid-upper and high-upper units. Drawers are only valid in lower units.
- **FR-008**: The engine MUST reject any unit definition that violates one or more manufacturability rules and return a list of all violations. Each error object MUST include `rule`, `offending_value`, and `limit` fields. Acceptance tests MUST assert on individual field values, not on message string content.
- **FR-009**: The engine MUST enforce the following validation rules as a minimum:
  - Shelf span (cm) must not exceed the material-specific maximum (sag prevention)
  - Drawer width must account for the required slide clearance per slide type
  - Minimum and maximum dimension guards must be enforced per part type (in cm)
  - Lower units (non-corner) must include exactly two stretchers — front (no groove) and back (with groove)
  - Drawers are only valid in lower units
- **FR-010**: Every generated part MUST carry a deterministic traceability identifier following the schema `[UNIT_ID]-[PART_ROLE]-[SEQUENCE]` (e.g., `CAB-001-LS-01`). The Unit ID is auto-generated by the engine as the next sequential identifier within the room, derived from the room context supplied by the caller.
- **FR-011**: Identical inputs (Workshop Profile + unit definition + room context) MUST always produce identical part sets with identical identifiers (full determinism — no timestamps, random seeds, or mutable state in the generation path).
- **FR-012**: The pytest test suite MUST include at least one test per assembly method resolver and at least one test per validation rule.
- **FR-013**: Unit definitions MUST be represented as immutable parameter sets; the engine MUST NOT mutate any input data.
- **FR-014**: All cabinet dimensions (W, H, D) and all generated part dimensions MUST be expressed in centimetres (cm).

### Key Entities

- **Workshop Profile**: The global settings entity passed to every engine call. Contains: `assembly_method` (`full_sides` | `full_top_bottom`), `carcass_thickness` (cm), `back_panel_thickness` (cm), `edge_banding_thickness` (cm). All engine functions MUST read from this profile — no hardcoded constants.
- **Unit Definition**: The full input to the engine — unit type (`lower` | `mid-upper` | `high-upper`), dimensions W × H × D in cm, configuration (shelves, drawers, corner flag). Immutable once submitted.
- **Room Context**: The ordered list of Unit IDs already assigned within the same room (e.g., `["CAB-001", "CAB-002"]`). The engine uses this to determine the next sequential Unit ID. In Phase 1 the caller (test or API layer) is responsible for supplying accurate room context.
- **Assembly Method**: A first-class domain concept (`full_sides` or `full_top_bottom`) stored in the Workshop Profile that governs which dimension resolver is applied. Changing this setting changes all panel dimensions across the entire workshop.
- **Part**: A single manufactured component within a unit. Has a role (e.g., left side, back panel, front stretcher, shelf), finished dimensions in cm, grain direction, edge banding assignments, and a traceability identifier.
- **Validation Rule**: A named, testable constraint. Each rule produces a typed error object when violated, carrying: `rule` (constraint name), `offending_value` (the submitted value that failed), and `limit` (the allowed threshold). All rules are evaluated before the engine returns.
- **Part Label**: The deterministic identifier assigned to each generated part, encoding unit ID, part role, and sequence number.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A valid lower unit definition (with a Workshop Profile) produces a complete, correctly dimensioned part set — including two stretchers — in a single engine call, verified by automated test against known-good expected outputs in cm.
- **SC-002**: Switching assembly method between `full_sides` and `full_top_bottom` on the Workshop Profile produces part dimensions that differ in exactly the ways each method dictates — verified by per-resolver tests.
- **SC-003**: Every invalid unit definition in the test suite is rejected with a complete list of all violated rules — each entry naming the rule, the offending value, and the allowed limit in cm. Zero silent failures, zero truncated error lists.
- **SC-004**: Running the engine on the same inputs (profile + definition + room context) ten consecutive times produces identical part sets and identical identifiers on every run — determinism verified by automated test.
- **SC-005**: The full test suite (both resolver tests + all validation rule tests) passes without a running server, database connection, or any external I/O — execution completes in under 60 seconds on a standard development machine.
- **SC-006**: A new team member can read the engine's domain models and understand what a lower unit is, what the Workshop Profile governs, what each assembly method produces, and how a part identifier is formed — without reading any implementation code.

## Assumptions

- Cabinet dimensions (W, H, D) are always provided in centimetres (cm). Material thickness values in the Workshop Profile are also in cm. No unit conversion is handled by the engine.
- The height dimension supplied in a unit definition is the net carcass height. The engine does not calculate or deduct toe kick or countertop allowance — those are handled outside the unit engine. Toe kick panels are standalone cut list items, not associated with any specific unit, and are out of scope for Phase 1.
- Door generation (slab dimensions, hinge hardware) is scoped to Phase 2 (hardware BOM). This phase generates the cabinet carcass parts only; door opening dimensions are recorded as attributes on the carcass.
- The engine has no HTTP interface in this phase — it is a pure Python library called directly by tests and, later, by the Phase 3 API layer.
- The back panel sits inside a routed groove on all four surrounding panels. Back panel dimensions and groove specifications are derived from the Workshop Profile thicknesses.
- All generated parts are immutable snapshots; there is no update or patch operation on a generated part in this phase.
- Nailers (site-fitted hanging strips) are out of scope. Stretchers (the two structural top rails on lower units) are generated parts and are in scope.
- Workshop Profile is supplied by the caller as an explicit input. In Phase 1 the engine does not load or persist a profile from any database.

## Clarifications

### Session 2026-05-16

- Q: Are nailers/hanging rails included in the engine's generated part set for this phase? → A: Out of scope — nailers are workshop-fitted site pieces, not generated parts in Phase 1. (Stretchers are different — they are structural carcass parts and are in scope.)
- Q: What is the required structure of a validation error returned by the engine? → A: Typed error object with `rule` (constraint name), `offending_value` (the failing value), and `limit` (the allowed threshold).
- Q: Is the Unit ID supplied by the caller or assigned by the engine? → A: Auto-generated by the engine from the room context (ordered list of existing Unit IDs in the same room supplied by the caller); engine assigns the next sequential ID.
- Q: Is the toe kick a generated part, a dimensional parameter, or neither? → A: Neither — toe kick is a standalone cut list item not associated with any unit. The engine does not calculate it. Cabinet height input is always the net carcass height.
- Q: When multiple validation rules are violated, does the engine fail fast or collect all violations? → A: Collect all — engine runs every rule and returns a list of all violations before stopping.

### Session 2026-05-16 (post-skill-review)

- Workshop Profile introduced as a mandatory third input to the engine — global settings (assembly method, carcass thickness, back panel thickness, edge banding thickness) — no hardcoded manufacturing constants permitted in the engine.
- Assembly method simplified to two options: `full_sides` (sides cover top/bottom) and `full_top_bottom` (top/bottom cover sides). Replaces the 5-joinery-method model from the original PLAN.MD.
- Unit type vocabulary updated from Base/Wall/Tall to `lower` / `mid-upper` / `high-upper`.
- Lower units always generate front and back stretchers (in place of a top panel), except corner units which have no stretchers.
- All dimensions (cabinet W/H/D and generated part dimensions) expressed in centimetres (cm).
- Material thickness reference (18mm) corrected to be profile-driven (1.855cm default), not hardcoded.
