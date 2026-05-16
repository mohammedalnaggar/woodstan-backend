# Tasks: Cabinet Domain Engine

**Input**: Design documents from `specs/001-cabinet-domain-engine/`

**Prerequisites**: plan.md ✓ spec.md ✓ research.md ✓ data-model.md ✓ contracts/engine_api.md ✓ quickstart.md ✓

**Tests**: Included — FR-011 explicitly requires at least one test per assembly method resolver and one per validation rule.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no inter-task dependencies)
- **[Story]**: Which user story this task belongs to
- All dimensions and values in cm. No hardcoded thickness constants in engine/.

---

## Phase 1: Setup

**Purpose**: Create the package skeleton and test harness. Nothing in later phases can start until directory structure and configuration are in place.

- [ ] T001 Create engine/ package directories with empty `__init__.py` files: `engine/`, `engine/models/`, `engine/resolvers/`, `engine/generators/`, `engine/validators/`
- [ ] T002 Create tests/ package directories with empty `__init__.py` files: `tests/`, `tests/resolvers/`, `tests/generators/`, `tests/validators/`
- [ ] T003 [P] Create `pyproject.toml` (or `pytest.ini`) at repo root — configure pytest test discovery for `tests/`, set `pythonpath = .` so `import engine` works from repo root
- [ ] T004 [P] Create `tests/conftest.py` with two shared fixtures: `default_profile` (assembly_method=full_sides, carcass=1.855cm, back=0.7cm, banding=0.1cm) and `full_top_bottom_profile` (same except assembly_method=full_top_bottom)

**Checkpoint**: `pytest tests/` runs with zero errors (no tests collected yet is fine).

---

## Phase 2: Foundational (Models)

**Purpose**: All typed dataclasses and enums that every other module depends on. Must be complete before ANY generator, resolver, or validator can be written.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T005 [P] Create `engine/models/profile.py` — `AssemblyMethod` enum (`full_sides`, `full_top_bottom`) and `WorkshopProfile` frozen dataclass (fields: assembly_method, carcass_thickness: float, back_panel_thickness: float, edge_banding_thickness: float)
- [ ] T006 [P] Create `engine/models/unit.py` — `UnitType` enum (`lower`, `mid_upper`, `high_upper`), `DrawerSlideType` enum (`side_slides`, `bottom_slides`), `DrawerConfig` frozen dataclass (position: int, slide_type), `UnitDefinition` frozen dataclass (unit_type, width, height, depth: float, shelf_count: int, drawers: tuple[DrawerConfig, ...], is_corner: bool, face_width_L: float | None, face_width_R: float | None); `is_corner` is valid for all unit types; `face_width_L/R` are None in Phase 1 and used for corner door widths in Phase 2
- [ ] T007 [P] Create `engine/models/part.py` — `PartRole` enum with all abbreviations from research.md (LS, RS, TP, BT, STF, STB, SH, BK, DV, DD, DSL, DSR, DWF, DWB), `EdgeBanding` frozen dataclass (top, left, bottom, right: bool), `Part` frozen dataclass (id, unit_id, role, length, width, thickness, quantity, grain_direction, edge_banding, groove, has_hinges)
- [ ] T008 [P] Create `engine/models/room.py` — `RoomContext` frozen dataclass (existing_unit_ids: tuple[str, ...])
- [ ] T009 [P] Create `engine/models/result.py` — `DimensionSet` frozen dataclass (inner_width, inner_height, shelf_width, shelf_depth, back_panel_width, back_panel_height, stretcher_width, stretcher_depth: float) and `GeneratedUnit` frozen dataclass (unit_id: str, unit_type: UnitType, parts: tuple[Part, ...])
- [ ] T010 [P] Create `engine/models/errors.py` — `ValidationError` frozen dataclass (rule: str, offending_value: float, limit: float, message: str) and module-level RULE_* string constants: RULE_SHELF_SPAN, RULE_DRAWER_NOT_PERMITTED, RULE_DRAWER_WIDTH_CLEARANCE, RULE_PART_BELOW_MIN, RULE_PART_ABOVE_MAX, RULE_STRETCHER_MISSING, RULE_STRETCHER_ON_CORNER
- [ ] T011 Update `engine/models/__init__.py` to re-export all public types from all model modules (single import surface for callers)

**Checkpoint**: `python -c "from engine.models import WorkshopProfile, UnitDefinition, Part, ValidationError"` runs without error.

---

## Phase 3: User Story 1 — Define and Validate a Lower Unit (Priority: P1) 🎯 MVP

**Goal**: A lower unit definition + Workshop Profile → complete validated part set (sides, bottom, stretchers, back, shelves, drawers) with correct cm dimensions and deterministic labels. The full generate_unit() round-trip works end-to-end.

**Independent Test**: `pytest tests/generators/test_lower_unit.py` passes — lower unit with one shelf produces exactly the expected part list with correct dimensions; running twice produces identical results.

### Implementation for User Story 1

- [ ] T012 [US1] Implement `resolve_dimensions()` for `full_sides` assembly in `engine/resolvers/full_sides.py` — compute inner_width=W−2T, inner_height=H−2T, shelf_width=W−2T−0.1, shelf_depth=D−3.0, back_panel dims=(inner_w+2×back_T, inner_h+2×back_T), stretcher_width=inner_width, stretcher_depth=10.0 (all from WorkshopProfile, no hardcoded constants)
- [ ] T013 [US1] Implement `resolve_dimensions()` dispatcher in `engine/resolvers/base.py` — reads `profile.assembly_method` and delegates to the correct resolver module; raises ValueError for unsupported method
- [ ] T014 [P] [US1] Implement all seven validation rule functions in `engine/validators/rules.py` — one function per RULE_* constant; each function receives (profile, unit, dimensions) and returns `ValidationError | None`; rules: shelf_span_exceeded (uses sag table from research.md), drawer_not_permitted, drawer_width_clearance (side slides: unit_w−4T−2.5 > 0; bottom: unit_w−4T−0.6 > 0), part_below_min_dimension, part_above_max_dimension, stretcher_missing (lower non-corner), stretcher_on_corner (corner unit)
- [ ] T015 [US1] Implement `validate_unit()` collect-all runner in `engine/validators/runner.py` — calls all rule functions, collects non-None results into a list, returns the full list (never stops early); function signature: `(profile, unit, dimensions) -> list[ValidationError]`
- [ ] T016 [P] [US1] Implement `assign_unit_id()` in `engine/generators/base.py` — derives next sequential ID from `room_context.existing_unit_ids`; `len(ids) + 1` zero-padded to 3 digits; e.g. 2 existing → `"CAB-003"`; pure function
- [ ] T017 [US1] Implement lower unit structural part generation in `engine/generators/lower.py` — `generate_lower_parts(profile, unit, dimensions, unit_id) -> list[Part]`: left side (LS-01), right side (RS-01), bottom panel (BT-01), front stretcher (STF-01, no groove, left edge banded), back stretcher (STB-01, groove=True, left edge banded), back panel (BK-01, no banding, no groove); apply correct EdgeBanding per part per skills/cabinet-specs/SKILL.md; all dimensions from DimensionSet
- [ ] T018 [P] [US1] Implement shelf generation in `engine/generators/shelves.py` — `generate_shelves(profile, unit, dimensions, unit_id) -> list[Part]`: generates `unit.shelf_count` shelf parts (SH-01, SH-02 …), each with length=shelf_depth, width=shelf_width, left edge banded only, no groove
- [ ] T019 [P] [US1] Implement upper unit structural part generation in `engine/generators/upper.py` — `generate_upper_parts(profile, unit, dimensions, unit_id) -> list[Part]`: left side (LS-01), right side (RS-01), top panel (TP-01, left edge banded), bottom panel (BT-01, left edge banded), back panel (BK-01); side panels banded on top+left+bottom (upper unit rule from SKILL.md)
- [ ] T020 [US1] Implement drawer box part generation in `engine/generators/drawers.py` — `generate_drawer_parts(profile, unit, dimensions, unit_id, drawer_door_height: float) -> list[Part]`: for each DrawerConfig, generate: DD (door, 4 edges banded), DSL + DSR (depth panels, 450cm fixed length... wait, 45cm — top edge only), DWF + DWB (width panels, side-slide: unit_w−4T−2.5, bottom-slide: unit_w−4T−0.6; top edge only); drawer body height = door_height − 2.0cm
- [ ] T021 [US1] Implement `generate_parts()` dispatcher in `engine/generators/base.py` — selects lower.py or upper.py based on unit_type, appends shelves, appends drawers (lower only); returns parts in stable order: structural panels → shelves → drawers; parts are a tuple for immutability
- [ ] T022 [US1] Implement `generate_unit()` entry point in `engine/__init__.py` — orchestrates: (1) resolve_dimensions, (2) validate_unit → return errors if non-empty, (3) assign_unit_id, (4) generate_parts → return GeneratedUnit; pure function, no I/O
- [ ] T023 [US1] Write `tests/generators/test_lower_unit.py` — test: lower unit (W=60, H=72, D=56, shelf_count=1, no drawers, is_corner=False) with default_profile → assert part count=6 (2 sides + bottom + 2 stretchers + back + 1 shelf = 7), assert STF-01 and STB-01 present, assert no TP part, assert all dimensions in cm match expected DimensionSet values
- [ ] T024 [P] [US1] Write `tests/generators/test_upper_unit.py` — test: mid-upper unit → assert TP-01 present, no STF/STB, no drawers accepted; test: high-upper unit → same assertions; test: drawer on mid-upper → returns validation error list not GeneratedUnit
- [ ] T025 [US1] Write `tests/generators/test_drawers.py` — test side-slide drawer width = W−4T−2.5; test bottom-slide drawer width = W−4T−0.6; test drawer body height = door_height−2.0; test depth panel length = 45.0cm (always)
- [ ] T026 [US1] Write determinism test in `tests/generators/test_lower_unit.py` — call generate_unit() 10× with identical inputs, assert all outputs equal the first result (part IDs, dimensions, quantities identical every time)

**Checkpoint**: `pytest tests/generators/ -v` all pass. US1 acceptance scenarios verified.

---

## Phase 4: User Story 4 — Validate Manufacturability Before Output (Priority: P2)

**Goal**: Every validation rule produces the correct typed error object (asserting rule name, offending_value, and limit individually). Collect-all mode confirmed — multiple violations return a full list.

**Independent Test**: `pytest tests/validators/test_rules.py -v` — one test per rule passes, each asserting exact field values (not message strings).

### Implementation for User Story 4

- [ ] T027 [P] [US4] Write `tests/validators/test_rules.py` — RULE_SHELF_SPAN: submit lower unit with shelf spanning 100cm (exceeds 90cm limit for 1.855cm thickness), assert `error.rule == RULE_SHELF_SPAN`, `error.offending_value == 100.0`, `error.limit == 90.0`
- [ ] T028 [P] [US4] Write test for RULE_DRAWER_NOT_PERMITTED — submit mid-upper unit with 1 drawer, assert `error.rule == RULE_DRAWER_NOT_PERMITTED`, `error.offending_value == 1`, `error.limit == 0`
- [ ] T029 [P] [US4] Write test for RULE_DRAWER_WIDTH_CLEARANCE — submit lower unit with width too narrow for side-slide drawer clearance, assert rule, offending_value (actual clearance in cm), limit (required clearance)
- [ ] T030 [P] [US4] Write test for RULE_PART_BELOW_MIN — submit unit with W=2.0cm (below 5cm guard), assert rule, offending_value=2.0, limit=5.0
- [ ] T031 [US4] Write collect-all test — submit definition with at least two simultaneous violations (e.g., shelf span + drawer not permitted on mid-upper), assert result is a list with exactly 2 ValidationError objects, one per rule; assert generate_unit() returns list not GeneratedUnit
- [ ] T032 [P] [US4] Write valid-definition test — submit a valid lower unit definition, assert `validate_unit()` returns an empty list

**Checkpoint**: `pytest tests/validators/ -v` all pass. Every RULE_* constant is covered by at least one test.

---

## Phase 5: User Story 2 — Resolve Dimensions by Assembly Method (Priority: P2)

**Goal**: `full_top_bottom` resolver implemented and tested. Switching assembly method on the Workshop Profile produces demonstrably different part dimensions for identical unit inputs.

**Independent Test**: `pytest tests/resolvers/ -v` — both resolver tests pass; comparison test asserts exact dimension differences between the two methods.

### Implementation for User Story 2

- [ ] T033 [US2] Implement `resolve_dimensions()` for `full_top_bottom` assembly in `engine/resolvers/full_top_bottom.py` — inner_width=W (full width, no deduction), inner_height=H−2T, shelf_width=W−0.1, shelf_depth=D−3.0; back panel and stretcher dims consistent with method; all values from WorkshopProfile
- [ ] T034 [P] [US2] Write `tests/resolvers/test_full_sides.py` — given default_profile (full_sides) + unit W=60 H=72 D=56, assert inner_width=60−(2×1.855)=56.29cm, inner_height=72−(2×1.855)=68.29cm, shelf_width=56.19cm, shelf_depth=53.0cm
- [ ] T035 [P] [US2] Write `tests/resolvers/test_full_top_bottom.py` — given full_top_bottom_profile + same unit, assert inner_width=60.0cm (no deduction), inner_height=68.29cm, shelf_width=59.9cm; confirm side panel height = inner_height (not H)
- [ ] T036 [US2] Write assembly method comparison test in `tests/resolvers/test_full_sides.py` — same unit definition run through both profiles; assert full_sides.inner_width < full_top_bottom.inner_width by exactly 2×carcass_thickness; assert full_sides.inner_height == full_top_bottom.inner_height (height deduction is the same for both methods)

**Checkpoint**: `pytest tests/resolvers/ -v` all pass. Both resolvers produce provably different dimensions.

---

## Phase 6: User Story 3 — Assign Deterministic Part Labels (Priority: P3)

**Goal**: Unit IDs are derived correctly from room context. Part label IDs follow the `[UNIT_ID]-[PART_ROLE]-[SEQUENCE]` schema. Identical inputs always produce identical identifiers.

**Independent Test**: `pytest tests/ -k "label or id or determinism" -v` — all label and ID tests pass.

### Implementation for User Story 3

- [ ] T037 [P] [US3] Write `tests/generators/test_lower_unit.py` — test assign_unit_id: empty room → `"CAB-001"`, 1 existing → `"CAB-002"`, 9 existing → `"CAB-010"`, assert zero-padding always 3 digits
- [ ] T038 [P] [US3] Write determinism test (10 runs) — same profile + unit + room_context → every run produces identical part IDs, lengths, widths, edge_banding values
- [ ] T039 [US3] Write part ID format test — lower unit with unit_id=`CAB-001` → assert left side id=`"CAB-001-LS-01"`, right side=`"CAB-001-RS-01"`, front stretcher=`"CAB-001-STF-01"`, back stretcher=`"CAB-001-STB-01"`, back panel=`"CAB-001-BK-01"`
- [ ] T040 [US3] Write sequential label test — unit with shelf_count=3 → assert ids are `"CAB-001-SH-01"`, `"CAB-001-SH-02"`, `"CAB-001-SH-03"` with no gaps; unit with 2 drawers → assert DD-01 and DD-02, DSL-01/DSL-02, DSR-01/DSR-02, DWF-01/DWF-02, DWB-01/DWB-02

**Checkpoint**: `pytest tests/ -v` — full suite passes. US3 label determinism confirmed.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Corner unit exception, hardcoded-constant audit, final suite validation.

- [ ] T041 [P] Write corner unit tests in `tests/generators/` — (a) lower unit with is_corner=True → assert no STF or STB parts in result, assert RULE_STRETCHER_MISSING is NOT triggered; (b) mid-upper unit with is_corner=True → assert carcass parts identical to non-corner mid-upper (is_corner has no carcass effect in Phase 1 for upper units); (c) assert face_width_L=None and face_width_R=None are accepted without error in Phase 1
- [ ] T042 [P] Run grep/search across `engine/` for any literal float matching known material constants (1.855, 0.7, 0.1, 18.55, 7.0) — confirm zero hardcoded constants outside `tests/conftest.py`; document findings
- [ ] T043 Verify full test suite runtime — `pytest tests/ -v --tb=short` completes in under 60 seconds; if not, identify slow tests and optimize
- [ ] T044 [P] Verify `engine/__init__.py` exports only `generate_unit` at the public surface — internal functions (resolve_dimensions, validate_unit, generate_parts) importable from submodules but not from `engine` directly
- [ ] T045 Review all function signatures in `engine/` for complete type annotations — add any missing return types; run `python -m py_compile engine/**/*.py` with no errors

**Checkpoint**: `pytest tests/ -v` — all tasks green, full suite under 60s, zero hardcoded constants in engine/.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 completion — **BLOCKS all user stories**
- **US1 (Phase 3)**: Depends on Phase 2 — includes resolvers, validators, generators, and entry point
- **US4 (Phase 4)**: Depends on Phase 3 (validators already implemented in T014/T015 — this phase adds test coverage)
- **US2 (Phase 5)**: Depends on Phase 3 (full_sides resolver in place — adds full_top_bottom and comparison tests)
- **US3 (Phase 6)**: Depends on Phase 3 (assign_unit_id and part generation already in place — adds label tests)
- **Polish (Phase 7)**: Depends on Phases 3–6 complete

### User Story Dependencies

- **US1 (P1)**: Requires models (Phase 2) — no other US dependency
- **US4 (P2)**: Requires US1 complete (validators implemented in Phase 3)
- **US2 (P2)**: Requires US1 complete (resolvers framework in place)
- **US3 (P3)**: Requires US1 complete (ID assignment and generators in place)
- **US4, US2, US3 can run in parallel** once Phase 3 is done

### Within Each User Story

- Models before resolvers → resolvers before validators → validators before generators → generators before entry point
- Tests can be written alongside or immediately after implementation (FR-011 requires tests; no strict TDD mandate)
- Collect-all validation (T015) must be complete before any round-trip test (T023) can pass

### Parallel Opportunities

- All Phase 2 model tasks (T005–T010) can run in parallel — different files, no inter-dependencies
- T014 (rules), T016 (assign_unit_id), T018 (shelves), T019 (upper) can run in parallel within Phase 3
- T024 (upper tests), T025 (drawer tests) can run in parallel within Phase 3
- T027–T032 (validation rule tests) can run in parallel within Phase 4
- T034, T035 (resolver tests) can run in parallel within Phase 5
- T037, T038 (label/ID tests) can run in parallel within Phase 6
- T041, T042, T044 can run in parallel within Phase 7

---

## Parallel Example: Phase 2 (Models)

```bash
# All six model files can be created simultaneously:
Task T005: engine/models/profile.py   — WorkshopProfile, AssemblyMethod
Task T006: engine/models/unit.py      — UnitDefinition, UnitType, DrawerConfig
Task T007: engine/models/part.py      — Part, PartRole, EdgeBanding
Task T008: engine/models/room.py      — RoomContext
Task T009: engine/models/result.py    — GeneratedUnit, DimensionSet
Task T010: engine/models/errors.py    — ValidationError, RULE_* constants
```

## Parallel Example: Phase 3 (US1)

```bash
# After T012 (full_sides resolver) and T013 (dispatcher) are complete:
Task T014: engine/validators/rules.py     — all validation rules
Task T016: engine/generators/base.py     — assign_unit_id()
Task T018: engine/generators/shelves.py  — shelf generation
Task T019: engine/generators/upper.py    — upper unit panels
```

---

## Implementation Strategy

### MVP (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Models (all T005–T011)
3. Complete Phase 3: US1 tasks T012–T026
4. **STOP and VALIDATE**: `pytest tests/generators/ -v` all pass
5. A full lower unit round-trip works end-to-end — this is the working MVP

### Incremental Delivery

1. Setup + Models → skeleton runs
2. US1 complete → full lower/upper unit generation working ← **demo point**
3. US4 complete → all validation rules fully tested
4. US2 complete → assembly method switching proven
5. US3 complete → label determinism confirmed
6. Polish → hardcoded constant audit, full suite timing

---

## Notes

- [P] tasks have no dependency on other incomplete tasks in the same phase — different files
- All dimensions in cm — if a value appears in mm in a comment or test, flag it immediately
- `frozen=True` on all dataclasses — if a mutation attempt appears during testing, it surfaces immediately
- Sag limit table from research.md must live in `engine/validators/rules.py` — not in a constants file that callers might hardcode
- Drawer depth panel length is 45.0cm (fixed hardware standard) — this is the one "magic number" that is permitted, and it must be named `DRAWER_DEPTH_PANEL_CM = 45.0` in drawers.py
