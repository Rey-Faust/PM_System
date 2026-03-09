[README.md](https://github.com/user-attachments/files/25837087/README.md)
# Unified PMO Control System

This package provides a unified PMO-style control system for multi-subproject delivery.

## What this system controls

The system is focused on control, not site micro-operations:

- Deviation control (scope/schedule/cost/procurement/resource/risk/collection)
- Interface and escalation control
- Cadence and closure control

## Data structure

### Core baselines

- `master_objectives.csv` (total schedule/budget/quality/collection/client targets)
- `escalation_matrix.csv` (site/subproject/PMO decision boundaries and escalation triggers)
- `subproject_registry.csv` (subproject registry and owners)

### MVP: 5 required tables

1. `pmo_master_control.csv` (cockpit output)
2. `weekly_progress.csv`
3. `cost_tracking.csv`
4. `procurement_tracking.csv`
5. `risk_issue_log.csv`

### Full module tables

- `scope_definition.csv`
- `weekly_progress.csv`
- `cost_tracking.csv`
- `procurement_tracking.csv`
- `resource_allocation.csv`
- `risk_issue_log.csv`
- `interface_register.csv`
- `meeting_decision_tracker.csv`
- `collection_tracking.csv`

## Quick start

1. Initialize working data files:

```bash
cd pmo
make init
```

2. Fill data in `pmo/data/*.csv` (weekly cadence recommended).

3. Build PMO cockpit:

```bash
cd pmo
make cockpit
```

4. Build weekly PMO digest (for control meeting):

```bash
cd pmo
make digest
```

5. Build full weekly pack in one command:

```bash
cd pmo
make weekly-pack
```

Output files:

- `pmo/data/pmo_master_control.csv`
- `pmo/data/pmo_weekly_digest.md`

## Status standard

Use `Green` / `Yellow` / `Red` in all status fields.

- `Green`: normal
- `Yellow`: at risk
- `Red`: deviated, requires escalation

## Suggested rhythm

- Daily: site stand-up and blocker update
- Weekly: subproject review + PMO control meeting + cost/procurement review
- Monthly: operating review (margin, collection, major risks)

Detailed operating rules are in `pmo/docs`.
