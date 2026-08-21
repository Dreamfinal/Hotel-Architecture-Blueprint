# Hotel Protocol vNext

Status: draft implementation contract on `vnext/runtime-neutral-hotel-protocol`.

This directory generalizes the original Hotel Architecture and the proven project prototypes into a Git-native, runtime-neutral protocol for disposable Guest workers.

## Core boundaries

- **Project truth lives in the Project Repo.** ChatGPT, Codex, Rin, local tools, and sessions are compute/runtime, not durable truth.
- **Hotel is not Rin.** Rin remains a separate local permanent-agent orchestration mode. Hotel must not depend on Rin mailbox, PID/watchers, wake commands, or a continuously running PC.
- **Guest is disposable.** A Guest does not need Team Repo, Staff memory, the whole project history, or the Hotel blueprint.
- **Room is the execution boundary.** A Room supplies the task, compiled context, skills, tools, authority, write scope, checks, acceptance criteria, and return contract needed for one bounded assignment.
- **One phase normally maps to one Hotel.** Durable project outcomes are absorbed into project source, `CURRENT_STATE.md`, `DECISION_LOG.md`, `DESIGN_SPEC.md`, or `ROADMAP.md`; temporary execution scaffolding is demolished after closure.

## Files

- `PROTOCOL.md` — architecture, state model, Project/Hotel layout, dependency-aware bases, and invariants.
- `GUEST_PROTOCOL.md` — minimal 10-step contract a fresh Guest must know.
- `CLAIM_PROTOCOL.md` — atomic fixed-ref claim, verification, stale recovery, and attempt history.
- `RETURN_PROTOCOL.md` — return evidence, review, acceptance, rework, and integration.
- `LIFECYCLE.md` — design/open/execute/review/close/demolish gates.
- `VALIDATION.md` — cross-file deterministic opening/closure/demolition checks.
- `PATH_RULES.md` — runtime-neutral read/write/return allowlist semantics.
- `schemas/HOTEL_MANIFEST.schema.json` — generic Hotel manifest schema.
- `schemas/ROOM_MANIFEST.schema.json` — generic Room manifest schema, including read-only Room support.
- `schemas/HOTEL_HISTORY.schema.json` — minimal audit record retained after demolition.
- `templates/RECEPTION.md` — human-readable Reception template.
- `templates/ROOM_START_HERE.md` — compiled one-Room Guest entry template.
- `tools/validate_hotel.py` — stdlib cross-file validator with no Team/runtime dependency.
- `examples/minimal-project/` — dependency-aware replayable example (`R001 → R002`).

The original root Blueprint remains historical/reference material while vNext is evaluated. vNext is designed so a Project may vendor the required protocol/schema/template/tool subset without granting Guests access to this repository.