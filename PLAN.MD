# Furniture Manufacturing Cut-List Platform

## Executive Summary & Delivery Phases

---

# 1. Executive Summary

The Furniture Manufacturing Cut-List Platform is a domain-specific manufacturing system designed to convert structured cabinet/unit definitions into production-ready cut lists for woodworking and cabinetry workshops.

The platform is NOT a CAD or 3D modeling tool. Instead, it functions as a deterministic manufacturing engine that transforms parametric furniture definitions into structured bill-of-materials outputs suitable for production and CNC workflows.

## Core Objective

To eliminate manual cut list preparation by automating the conversion of cabinet specifications into accurate, standardized manufacturing outputs.

## Key Capabilities

* Define furniture units using structured parameters (width, height, depth, configuration)
* Import cabinet definitions from external systems (e.g., Blender JSON exports)
* Generate complete cut lists for all cabinet components
* Include manufacturing metadata such as:

  * Material type
  * Panel dimensions
  * Grain direction
  * Edge banding rules
  * Hardware operations
* Export production-ready outputs (CSV / JSON / future CNC formats)

## System Philosophy

* Structured data is the source of truth (not geometry)
* Manufacturing rules must be deterministic and repeatable
* Every generated part must be traceable to its origin unit
* The system prioritizes correctness and manufacturability over visualization

---

# 2. High-Level Architecture Overview

The system is structured as a pipeline:

```
Input (Unit Definitions)
        ↓
Rule Engine (Manufacturing Logic)
        ↓
Part Generation Engine
        ↓
Cut List Aggregation
        ↓
Export Layer (CSV / JSON)
```

---

# 3. Delivery Phases

## Phase 0 — Constitution & Domain Foundation

Defines the system’s fundamental principles and domain language.

### Objectives

* Establish manufacturing terminology
* Define system boundaries (non-CAD system)
* Define architectural principles
* Define core constraints and assumptions

### Outputs

* Domain vocabulary (Unit, Cabinet, Part, Material, etc.)
* System principles and constraints
* High-level architecture rules

---

## Phase 1 — Cabinet Domain Engine (Core Logic)

Implements the core transformation engine from cabinet definitions to parts.

### Objectives

* Define cabinet schemas
* Implement rule-based part generation
* Support base cabinet as initial model

### Outputs

* Cabinet data models
* Part generation engine
* Deterministic dimension calculations

### Acceptance Criteria

A base cabinet input produces a complete set of manufacturing parts with correct dimensions and metadata.

---

## Phase 2 — Cut List Engine

Standardizes generated parts into manufacturing-ready outputs.

### Objectives

* Normalize part structures
* Add manufacturing metadata (grain, edge banding, operations)
* Enable grouping and aggregation

### Outputs

* Structured cut list model
* CSV/JSON export capability

---

## Phase 3 — Project & Unit Management Layer

Introduces multi-unit and project-level organization.

### Objectives

* Manage multiple cabinets per project
* Organize units into rooms/projects
* Enable batch processing

### Outputs

* Project structure
* Unit management APIs
* Aggregated cut list generation

---

## Phase 4 — Frontend Operational Dashboards

Provides UI for interacting with the system.

### Objectives

* Build operational dashboards (not CAD UI)
* Enable fast unit definition and cut list review
* Provide spreadsheet-like experience

### Screens

* Projects Dashboard
* Unit Builder Dashboard
* Cut List Dashboard
* Materials & Rules Dashboard

---

## Phase 5 — Blender Integration Layer

Enables import of structured cabinet definitions from Blender.

### Objectives

* Import JSON exports from Blender
* Validate cabinet definitions
* Convert into internal unit schema

### Constraints

* No geometry parsing
* Only semantic data import

---

## Phase 6 — Rules Configuration System

Externalizes manufacturing logic into configurable rules.

### Objectives

* Define material rules
* Define cabinet construction rules
* Define hardware and edge banding rules

### Outputs

* Configurable rule engine
* Editable manufacturing standards

---

## Phase 7 — Costing & Quotation Engine

Introduces business-level outputs for pricing and estimation.

### Objectives

* Material cost estimation
* Hardware cost calculation
* Labor estimation
* Profit margin calculation

### Outputs

* Quotation reports
* Cost breakdowns per project

---

## Phase 8 — Optimization Engine (Future)

Implements sheet optimization and nesting logic.

### Objectives

* Optimize material usage
* Reduce waste
* Generate sheet layouts

### Outputs

* Optimized cut layouts
* Sheet utilization reports

---

# 4. Key Architectural Principles

* Structured data is the system of record
* Geometry is optional and secondary
* All outputs must be deterministic
* Manufacturing constraints are first-class logic
* System must remain extensible for CNC integration

---

# 5. Long-Term Vision

The platform evolves into a full manufacturing intelligence system covering:

* CNC integration
* Production tracking
* Inventory management
* Supplier integration
* Automated workshop operations
