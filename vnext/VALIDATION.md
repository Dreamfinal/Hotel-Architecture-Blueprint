# Deterministic Hotel Validation

Schema validation is necessary but not sufficient. A Hotel may conform to JSON Schema and still be unsafe to open.

## Hotel-level validation

A validator must fail opening when any of these are true:

1. Hotel/Room manifest JSON is invalid or unknown required schema version.
2. Hotel ID in a Room differs from its parent Hotel.
3. Room IDs are duplicated or manifest paths do not exist.
4. A dependency references a missing Room.
5. The dependency graph contains a cycle.
6. A Room depends on itself.
7. A Room marked `READY` has unresolved/null `claim_base_sha`.
8. A `claim_base_sha` or `hotel_base_sha` does not resolve to a commit reachable/available to the execution substrate.
9. Required Room input or Room-local skill paths are missing.
10. A path is both forbidden by project policy and allowlisted by a Room.
11. Two simultaneously dependency-ready Rooms have overlapping production `write_allowlist` paths without an explicit serialization dependency/coordinator-owned integration exception.
12. A Room's return report path is not covered by `return_allowlist`.
13. Reception lists a Room as dependency-ready when its dependencies are not accepted/materialized.
14. Reception omits a dependency-ready Room without an explicit hold/block reason.
15. Claim prefix does not match the Hotel ID or collides with active state from another Hotel instance.
16. `claims_enabled=true` while lifecycle is anything other than `OPEN`.
17. lifecycle is `OPEN` while `claims_enabled=false`, unless an explicit closing transition is being committed atomically.
18. project `CURRENT_STATE.md` points to a different active Hotel/phase at opening time.

## Write overlap semantics

Path overlap must account for ancestor/descendant relationships, not only literal equality.

Examples that conflict:

```text
src/features/
src/features/map/index.ts
```

```text
src/App.tsx
src/App.tsx
```

Two Rooms may read the same source. They may not concurrently write the same production surface unless the Hotel explicitly serializes them.

Return-only paths under different Room packets do not count as production write conflicts.

## Dependency-ready calculation

A Room is dependency-ready iff:

```text
logical_state in {READY, REWORK}
AND all depends_on Rooms are ACCEPTED
AND dependency outputs required by this Room are materialized
AND claim_base_sha is resolved
AND no explicit coordinator hold exists
```

Live occupancy is then determined separately from the fixed remote claim ref.

## Claim/ref checks at opening

Before opening:

- no fixed active claim ref may already exist for a Room in this new Hotel instance;
- retained archive refs must use a different namespace from active claim refs;
- the configured integration ref must resolve;
- every initially READY Room's base must be compatible with the integration plan.

## Closure validation

Before `CLOSED`:

- all required Rooms are `ACCEPTED` or explicitly waived in durable project decisions;
- accepted outputs are integrated/materialized;
- no accepted output exists only on a temporary claim branch;
- current project state and decisions are refreshed;
- the proposed history record matches Hotel ID, phase, base, final integration/source commit, accepted/waived Rooms, and retention outcome.

## Demolition validation

Before removing execution scaffolding:

- Hotel is `CLOSED`;
- claims are disabled;
- required claim/attempt tips are preserved according to retention policy;
- `hotels/history/<hotel-id>.json` exists and is committed;
- `CURRENT_STATE.md` no longer presents the Hotel as active after the demolition commit;
- deletion set contains only approved temporary Hotel material.

Validation is deterministic evidence. It does not replace domain review of Room outputs.