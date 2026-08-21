# Deterministic Hotel Validation

Schema validation is necessary but not sufficient. Hotel vNext uses layered validation so a design can be checked before real Git refs exist without confusing that with authorization to open.

## 1. Structural validation

Run against a checkout of the intended control packet:

```text
python vnext/tools/validate_hotel.py <hotel-dir>
```

This checks cross-file invariants including:

- Hotel/Room IDs and standard manifest/entry paths;
- dependency references, exact edge agreement, self-dependency, and cycles;
- logical readiness and resolved base shape for claimable Rooms;
- compiled Room input/skill packet locations and required existence when claimable;
- repo-relative path safety, traversal/symlink escape, and no glob semantics;
- Hotel-wide `forbidden_write_paths` vs Room production/return writes;
- simultaneous claimable-Room production write overlap;
- return-report coverage by return allowlist;
- dependency-ready Rooms present in Reception;
- root `CURRENT_STATE.md` existence.

Structural success means the packet is internally coherent. It does **not** prove that Git refs/SHA values exist or that remote claim branches are vacant.

## 2. Git opening validation

Before a real opening, run from the exact local checkout of the Hotel's `control_ref`:

```text
python vnext/tools/validate_hotel.py <hotel-dir> --check-git-refs
```

In addition to structural checks, this verifies:

- checkout `HEAD` equals the resolved local `control_ref` head;
- `hotel_base_sha` resolves to a commit;
- every non-null Room `claim_base_sha` resolves to a commit;
- `integration_ref` resolves to a commit;
- each claimable `source_read_allowlist` path exists in that Room's `claim_base_sha` tree.

Compiled `inputs/` and Room-local `skills/` are validated on the control checkout because they belong to the pinned control packet, not the claim code-base commit.

## 3. Remote opening checks

The coordinator/opening implementation must additionally verify against the remote substrate immediately before enabling claims:

- intended `control_ref` and `integration_ref` remote tips match the commits just validated/pushed under project policy;
- no fixed active claim ref exists under this new Hotel's `claim_prefix`;
- retained archive/attempt refs use a different namespace;
- no stale prior Hotel instance collides with the same Hotel ID/ref namespace;
- project `CURRENT_STATE.md` identifies the intended active Hotel/control pointer;
- the opening control commit is remotely visible before any Guest receives claim permission.

These checks require remote Git/GitHub state and are intentionally not faked by structural validation.

## 4. Write overlap semantics

Path overlap accounts for ancestor/descendant relationships, not only literal equality.

Examples that conflict:

```text
src/features/
src/features/map/index.ts
```

```text
src/App.tsx
src/App.tsx
```

Two Rooms may read the same source. They may not concurrently write the same production surface. If a temporary hold is needed, represent that Room as `BLOCKED` rather than pretending it is READY.

Return-only paths under distinct Room packets normally do not conflict, but they are still subject to Hotel-wide forbidden write paths.

## 5. Dependency-ready calculation

A Room is dependency-ready iff:

```text
logical_state in {READY, REWORK}
AND all depends_on Rooms are ACCEPTED
AND dependency outputs required by this Room are integrated/materialized
AND required compiled Room inputs exist on control plane
AND claim_base_sha is resolved
```

Live occupancy is then determined separately by the fixed remote claim ref.

## 6. Dual-pin validation

A real Guest contract uses:

- `control_commit_sha`: exact control-ref commit containing Reception/Room packet;
- `claim_base_sha`: exact project code/integration commit used to create the claim branch.

The manifest declares `claim_base_sha`; the Guest derives and records `control_commit_sha` from the fetched control-ref head. This avoids impossible Git self-reference while pinning both contract and code.

## 7. Closure validation

Before `CLOSED`:

- all required Rooms are `ACCEPTED` or explicitly waived by durable owner decision;
- accepted outputs are integrated/materialized;
- no accepted output exists only on a temporary claim branch;
- current project state and decisions are refreshed;
- Room acceptance records preserve control/base/head/integration evidence;
- the proposed Hotel history matches Hotel ID, phase, base, final control/integration commits, Room results/waivers, and retention outcome.

## 8. Demolition validation

Before removing execution scaffolding:

- Hotel is `CLOSED` and claims are disabled;
- required claim/attempt tips are preserved according to retention policy;
- `hotels/history/<hotel-id>.json` exists and is committed;
- `CURRENT_STATE.md` no longer presents the completed Hotel as active after demolition;
- deletion set contains only approved temporary Hotel material.

Validation is deterministic evidence. It does not replace domain review of Room outputs.