# Hotel Protocol vNext — Core Contract

## 1. Purpose

Hotel is a Git-native execution protocol for disposable Guest workers. One bounded project phase becomes Rooms that can be claimed, executed, returned, reviewed, integrated, closed, and demolished without persistent chat context or permanent Guest identity.

A correct Hotel optimizes for **small context + explicit authority + durable evidence + safe concurrency**.

## 2. Project layout

A migrated Project Repo keeps durable project truth at root:

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

`hotels/<hotel-id>/` is temporary execution/control scaffolding. `hotels/history/<hotel-id>.json` is the minimal durable completion/audit record retained after demolition.

## 3. Durable project truth

- `DESIGN_SPEC.md`: what the project/product is.
- `ROADMAP.md`: durable phase structure and future direction.
- `CURRENT_STATE.md`: current phase, active Hotel/control pointer, blockers, next action, and canonical pointers.
- `DECISION_LOG.md`: durable decisions and rationale.
- project source/artifacts: actual accepted output.
- while Hotel exists: its control-plane manifests/Reception and accepted integration commits are durable execution evidence.

Chat history, Staff memory, Rin envelopes, local worktrees, copied prompts, generated scratch, and unintegrated Guest reports are not canonical project truth.

## 4. Three Git anchors

See `CONTROL_PLANE.md` for the full control contract.

### `hotel_base_sha`

Immutable audit origin where Hotel construction began.

### `control_ref`

Moving authoritative ref for Hotel lifecycle, Reception, Room manifests, compiled Room inputs/skills, dependency readiness, and resolved Room bases.

A Guest always fetches the latest remote `control_ref` before selecting work and records its exact head as `control_commit_sha`.

### `integration_ref`

Moving ref/line where coordinator-reviewed accepted production output is materialized.

`control_ref` and `integration_ref` may be the same ref in a simple project, but their responsibilities remain distinct.

## 5. Dual-pin Guest contract

Every active Guest run is bound to:

```text
control_commit_sha
= exact immutable Room contract/context snapshot

claim_base_sha
= exact immutable project code/integration base
```

The Room manifest declares `claim_base_sha` on the control plane. The Guest derives `control_commit_sha` from the fetched control-ref head.

This separation is required: putting a manifest inside the same commit whose hash it declares as its own base would create impossible Git self-reference.

### Read locations

From `control_commit_sha`:

- `RECEPTION.md`;
- `ROOM_MANIFEST.json`;
- `START_HERE.md`;
- compiled Room `input/`;
- Room-local `skills/`.

From the claim branch initialized at `claim_base_sha`:

- project paths in `source_read_allowlist`;
- production paths in `write_allowlist`;
- Room return/claim evidence allowed by `return_allowlist`.

Later control/integration movement cannot silently change an already-claimed Guest's contract or code base.

## 6. Hotel lifecycle

```text
DRAFT → VALIDATED → READY_TO_OPEN → OPEN → CLOSING → CLOSED → DEMOLISHED
```

- `DRAFT`: Hotel/Rooms may change; claims forbidden.
- `VALIDATED`: schema + cross-file structural validation pass.
- `READY_TO_OPEN`: control packet is complete enough to open; initially-ready Room bases/inputs are resolved.
- `OPEN`: opening control commit is remotely verified and `claims_enabled=true`.
- `CLOSING`: claims disabled first; returns/review/integration reconcile.
- `CLOSED`: required Rooms accepted/integrated or explicitly waived and project truth refreshed.
- `DEMOLISHED`: approved temporary control/claim/worktree material removed; minimal Hotel history remains.

Room logical lifecycle:

```text
DRAFT → BLOCKED / READY → CLAIMED → IN_PROGRESS → RETURNED → REVIEW
                                                       ↘ ACCEPTED
                                                       ↘ REWORK → READY
                                                       ↘ BLOCKED
```

`STALE` is a derived abandoned-claim condition handled only by coordinator/housekeeping recovery.

## 7. Dependency model

Room dependencies form a DAG. A Room becomes `READY` only when:

1. every `depends_on` Room is `ACCEPTED`;
2. required upstream output is integrated/materialized;
3. required dependency context is compiled into this Room's control-plane `input/` packet;
4. Room `claim_base_sha` resolves to the intended code/integration commit;
5. required source paths exist in that claim-base tree;
6. Room authority/write scope remains safe against other simultaneously-ready Rooms;
7. control-plane validation passes.

### Downstream transition

After upstream acceptance, coordinator:

1. integrates output on `integration_ref`;
2. compiles downstream packet context on `control_ref`;
3. sets downstream `claim_base_sha` to the relevant integration commit;
4. changes Room from `BLOCKED` to `READY`;
5. refreshes Reception;
6. pushes/verifies the new control commit.

A fresh Guest can claim the downstream Room only after that verified control transition.

## 8. Reception

Reception is the compact Guest-facing front desk on `control_ref`. It contains only:

- Hotel ID, `control_ref`, phase objective;
- lifecycle + claims enabled state;
- claim prefix/procedure pointer;
- dependency-ready Rooms with one-line objective/entry path;
- blocked Rooms with short blocker/dependency reason;
- instruction not to load Team Repo, project history, Blueprint, or unrelated Rooms.

Reception is dependency-readiness/control evidence, not occupancy lock. **Fixed remote claim refs are authoritative for live occupancy.**

## 9. Room packet

A Room packet is architect-compiled context, not a raw project dump. It defines:

- measurable objective;
- dependencies + `claim_base_sha`;
- compiled `input/` paths on control plane;
- project `source_read_allowlist` on claim base;
- Room-local skills on control plane;
- tool capability requirements;
- allowed/forbidden authority;
- Hotel-wide forbidden writes + Room write/return allowlists;
- deterministic checks;
- acceptance criteria;
- reviewer/next routing;
- required return fields/evidence;
- escalation conditions.

A fresh Guest must not need Team Repo or unrelated project/Hotel context to execute it.

## 10. Skills, tools, and authority

Room Skills are copied/compiled into the Project/Room packet. Guests must not need Team Repo access.

Tool access never grants authority. Effective authority is:

```text
Project policy
∩ Hotel policy
∩ Hotel forbidden-write boundary
∩ Room authority
∩ Room read/write/return allowlists
∩ owner/runtime safety constraints
```

Unavailable required capability produces an authorized `IMPLEMENTED_UNVERIFIED` or `BLOCKED` return; never fabricated validation.

## 11. Concurrency

Default rule: simultaneously claimable Rooms must not have overlapping production write allowlists.

If overlap is unavoidable, serialize those Rooms through dependency/block state or use a coordinator-owned integration surface Guests cannot edit.

Rooms may read the same source. Packet inputs/skills are read-only. Accepted dependency outputs are read-only to downstream Rooms unless explicitly allowlisted for modification.

## 12. Claim / return / acceptance

Claim branch:

```text
hotel/<hotel-id>/claims/<room-id>
```

Non-force creation from `claim_base_sha` is the atomic occupancy lock and working/return branch. Claim record preserves `control_ref`, `control_commit_sha`, and `claim_base_sha`.

Guest return preserves the same dual pins + final head and evidence. Reviewer reloads the exact Room contract from the pinned control commit.

```text
push != acceptance
acceptance != integration
integration != downstream readiness
integration != Hotel closure
```

See `CLAIM_PROTOCOL.md` and `RETURN_PROTOCOL.md`.

## 13. Current state and closure

While a Hotel is active, root `CURRENT_STATE.md` identifies the active Hotel/control pointer and next coordinator/owner action. It does not duplicate Room transcripts/occupancy.

Before closure, accepted durable output/state is absorbed into project source and, when relevant, `CURRENT_STATE.md`, `DECISION_LOG.md`, `DESIGN_SPEC.md`, or `ROADMAP.md`.

After closure gates pass, demolition retains `hotels/history/<hotel-id>.json` with per-Room control/base/head/integration evidence and removes temporary material according to retention policy.

## 14. Runtime portability

```text
Project Repo
  ├─ ChatGPT Guest → GitHub control/claim refs + files
  └─ Codex Guest   → local Git/GitHub control/claim refs + files
```

Both obey the same control snapshot, Room manifest, claim namespace, source/write boundaries, return contract, and review state. Runtime switching does not rewrite project state.

## 15. Non-goals

Hotel vNext does not require:

- Rin runtime;
- permanent Guest identity/memory;
- an always-on local process;
- GitHub Actions;
- a central LLM orchestrator;
- Team Repo access by Guests.

Actions/scheduled tasks may optionally validate/observe state, but Git/GitHub Project state remains authoritative.