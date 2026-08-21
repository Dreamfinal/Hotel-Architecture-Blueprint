# Hotel Protocol vNext — Core Contract

## 1. Purpose

Hotel is a Git-native execution protocol for disposable Guest workers. It turns one bounded project phase into Rooms that can be claimed, executed, returned, reviewed, integrated, closed, and demolished without requiring persistent chat context or permanent agent identity.

A correct Hotel optimizes for **small context + explicit authority + durable evidence + safe concurrency**.

## 2. Project layout

A migrated Project Repo keeps durable truth at root:

```text
Project/
├─ AGENTS.md
├─ DESIGN_SPEC.md
├─ ROADMAP.md
├─ CURRENT_STATE.md
├─ DECISION_LOG.md
├─ source / product files...
└─ hotels/
   ├─ <hotel-id>/
   │  ├─ HOTEL_MANIFEST.json
   │  ├─ RECEPTION.md
   │  └─ rooms/
   │     ├─ R001/
   │     │  ├─ ROOM_MANIFEST.json
   │     │  ├─ START_HERE.md
   │     │  ├─ input/
   │     │  ├─ skills/
   │     │  └─ return/
   │     └─ R002/...
   └─ history/
      └─ <hotel-id>.json
```

`hotels/<hotel-id>/` is execution scaffolding. `hotels/history/<hotel-id>.json` is the minimal durable completion/audit record left after demolition.

## 3. Durable sources of truth

- `DESIGN_SPEC.md`: what the project/product is.
- `ROADMAP.md`: durable phase structure and future direction.
- `CURRENT_STATE.md`: current phase, active Hotel, work in progress, blockers, next action, and pointers.
- `DECISION_LOG.md`: durable decisions and rationale.
- project source/artifacts: actual accepted output.
- `HOTEL_MANIFEST.json`: one Hotel's execution contract while that Hotel exists.
- `ROOM_MANIFEST.json`: one Room's execution contract while that Room exists.

Chat history, Staff memory, Rin envelopes, local worktrees, generated prompts, and temporary Guest reports are not canonical project truth.

## 4. Hotel state model

Hotel lifecycle:

```text
DRAFT
  ↓
VALIDATED
  ↓
READY_TO_OPEN
  ↓
OPEN
  ↓
CLOSING
  ↓
CLOSED
  ↓
DEMOLISHED
```

- `DRAFT`: architecture may change; claims forbidden.
- `VALIDATED`: manifests, graph, inputs, authority, paths, and schema pass validation.
- `READY_TO_OPEN`: immutable/pinned opening inputs are prepared and baseline/integration refs exist.
- `OPEN`: `claims_enabled=true`; dependency-ready Rooms may be claimed.
- `CLOSING`: no new claims; outstanding returns/reviews/integration are reconciled.
- `CLOSED`: all required Rooms are accepted/integrated and closure evidence is complete.
- `DEMOLISHED`: temporary Hotel packets/refs/worktrees are removed under retention policy; minimal history + project truth remain.

Room logical lifecycle:

```text
DRAFT → BLOCKED / READY → CLAIMED → IN_PROGRESS → RETURNED → REVIEW
                                                       ↘ ACCEPTED
                                                       ↘ REWORK → READY
                                                       ↘ BLOCKED
```

Execution may additionally derive `STALE` from an abandoned claim. Recovery is a coordinator/housekeeping action, not a Guest action.

## 5. Dependency model

Rooms form a directed acyclic work graph unless the Hotel explicitly declares an iteration loop outside the dependency graph.

A Room becomes `READY` only when:

1. every `depends_on` Room is `ACCEPTED`;
2. required dependency output has been integrated/materialized into the Hotel integration ref or compiled into this Room's input packet;
3. the Room's `claim_base_sha` is resolved;
4. source/context inputs exist;
5. its write scope does not conflict with any concurrently claimable Room;
6. opening/Room validators pass.

### Hotel baseline vs Room claim base

`hotel_base_sha` is the immutable starting point for Hotel construction/audit.

`claim_base_sha` is per Room. For independent Rooms it may equal `hotel_base_sha`. For dependent Rooms it may be a later integration commit containing accepted dependency output.

This preserves a stable Hotel origin while allowing downstream Rooms to consume accepted upstream work without rebuilding the Hotel.

## 6. Reception

`RECEPTION.md` is the Guest-facing front desk. It must be compact and contain only:

- Hotel ID / phase objective;
- lifecycle and whether claims are enabled;
- claim prefix and claim procedure pointer;
- Rooms that are dependency-ready, with one-line objective and Room entry path;
- blocked Rooms with only their blocking Room IDs/reason;
- explicit instruction not to load Team Repo, whole project history, Blueprint, or unrelated Rooms.

Reception is not the authoritative occupancy lock. **Remote claim refs are authoritative for occupancy.** A Guest may perform one prefix-filtered remote claim listing after reading Reception.

## 7. Room packet

A fresh Guest must be able to execute a Room from:

1. root `AGENTS.md` only to learn project-wide safety that applies to all work;
2. `RECEPTION.md`;
3. the claimed Room `START_HERE.md`;
4. the Room manifest and its declared inputs/skills/source paths.

A Room packet compiles context rather than dumping raw project history. It must specify:

- measurable objective;
- `depends_on` and `claim_base_sha`;
- input/context files;
- read/source allowlist;
- write allowlist;
- Room-local skill payloads;
- tool requirements and runtime capability assumptions;
- allowed/forbidden authority;
- deterministic checks;
- acceptance criteria;
- reviewer/return routing;
- required return artifacts/evidence;
- escalation conditions.

## 8. Skills and tools

Room Skills are copied/compiled into the Project/Room packet. A Guest must not require Team Repo access to use them.

Tool availability does not grant authority. A Room may say a tool is required or optional, but authority is the intersection of:

```text
Project policy
∩ Hotel policy
∩ Room authority
∩ write/read allowlists
∩ owner/runtime safety constraints
```

If a runtime lacks a required tool, the Guest returns `BLOCKED` or an explicitly allowed `IMPLEMENTED_UNVERIFIED`; it must not invent validation evidence.

## 9. Concurrency and write ownership

Default policy is **no overlapping write allowlists among simultaneously claimable Rooms**.

If overlap is unavoidable, the Hotel must serialize those Rooms through dependencies or declare a coordinator-owned integration surface that Guests cannot edit directly.

Room source inputs are read-only unless also explicitly allowlisted for write.

## 10. Return and review

A Guest returns through the same claim branch. Required evidence includes at least:

- room/hotel IDs;
- claim/session identifier;
- claim base and head commit;
- changed paths;
- write-allowlist self-check;
- checks actually run + exit/result;
- checks not run and why;
- output paths;
- unresolved risks/contradictions;
- requested next state.

Only the designated reviewer/coordinator may mark a Room `ACCEPTED` and integrate it. A successful push is delivery evidence, not acceptance.

## 11. Project current state

While a Hotel is active, root `CURRENT_STATE.md` points to the active Hotel/phase and states the next coordinator/owner action. It must not duplicate Room-by-Room transcripts.

When the Hotel closes, accepted durable outcomes are reflected in source, `CURRENT_STATE.md`, `DECISION_LOG.md`, `DESIGN_SPEC.md`, and/or `ROADMAP.md` as appropriate before demolition.

## 12. Runtime portability

The contract is runtime-neutral:

```text
Project Repo
  ├─ ChatGPT Guest → GitHub refs/files
  └─ Codex Guest   → local Git/GitHub refs/files
```

Both paths obey the same Room manifest, claim ref namespace, allowlists, return contract, and review states. No architecture rewrite is required when switching runtime.

## 13. Non-goals

Hotel vNext does not require:

- Rin runtime;
- permanent Guest identity/memory;
- a local always-on process;
- GitHub Actions;
- a central LLM orchestrator;
- Team Repo access by Guests.

Optional Actions/scheduled tasks may later observe or validate Hotel state, but Git/GitHub project state remains authoritative.