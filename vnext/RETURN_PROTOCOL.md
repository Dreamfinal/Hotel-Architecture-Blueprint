# Room Return and Acceptance Protocol

## Guest return

A Room return is delivered on the Room's fixed claim branch. It is not accepted merely because it was pushed.

The canonical machine-readable return is:

```text
hotels/<hotel-id>/rooms/<room-id>/return/ROOM_RETURN.json
schema_version: return-vnext-0.1
```

Use `schemas/RETURN.schema.json` and `templates/ROOM_RETURN.json`. A project may additionally retain human-readable notes/evidence under the Room return allowlist, but those do not replace the JSON return record.

The return identifies the immutable Room-contract snapshot and code base used for implementation:

```text
hotel_id
room_id
claim_id
session_id
control_ref
control_commit_sha
claim_base_sha
implementation_commit_sha?   # optional, only if known before final return metadata commit
status
changed_paths
allowlist_self_check
implemented_contract
checks_run
checks_unrun
output_paths
unresolved
requested_next_state
```

`ROOM_RETURN.json` deliberately does **not** declare the SHA of the commit that contains itself. The final remote claim-branch head is reviewer-derived evidence named `return_head_sha`.

`control_commit_sha` pins the exact Reception/Room packet/skills/criteria the Guest followed. `claim_base_sha` pins the project code/integration tree from which the working claim branch began.

Valid Guest-return statuses are:

- `RETURNED` — implementation/output completed and available required checks were run; request `REVIEW`;
- `IMPLEMENTED_UNVERIFIED` — bounded implementation completed but declared validation capability was unavailable; request `REVIEW` or `REWORK` according to Room/project policy;
- `BLOCKED` — objective cannot be completed within current inputs/authority/dependencies; request `BLOCKED`.

A Guest must never self-assign `ACCEPTED`.

## Reviewer sequence

The designated reviewer/coordinator:

1. resolves the exact remote fixed claim ref and records its current head as `return_head_sha`;
2. reads `ROOM_RETURN.json` from that exact returned head and validates it against `RETURN.schema.json`;
3. verifies claim branch identity, `control_commit_sha`, `claim_base_sha`, and claim/session IDs;
4. reloads the Room contract from the pinned control commit rather than a newer moving control ref;
5. computes the actual diff from `claim_base_sha` to `return_head_sha`;
6. verifies every actual changed path against that contract's production + return allowlists and Hotel-wide forbidden paths;
7. checks that self-reported `changed_paths` matches the actual diff (order need not matter), so omitted files cannot hide scope expansion;
8. verifies declared deterministic evidence or reruns checks in an authorized runtime;
9. reviews every acceptance criterion from the pinned control packet;
10. checks domain/UX/quality criteria that cannot be reduced to exit codes;
11. records verdict `ACCEPTED`, `REWORK`, or `BLOCKED` with evidence;
12. integrates/materializes accepted output through the Hotel integration path;
13. records accepted `return_head_sha` + integration/source commit;
14. compiles dependency output needed by downstream Rooms, resolves newly-ready Room `claim_base_sha` values, and refreshes Room manifests/Reception on `control_ref`;
15. verifies the remote control commit before exposing newly-ready Rooms to Guests.

## Acceptance invariant

```text
push != valid return
valid return != acceptance
check pass != domain acceptance
acceptance != integration
integration != downstream readiness
integration != Hotel closure
```

Each transition requires explicit evidence.

## Rework

A rework preserves the same Room identity but may create a new control snapshot and/or code base.

The coordinator may preserve/archive the prior attempt, reset the active claim according to `CLAIM_PROTOCOL.md`, update compiled inputs/criteria if necessary, resolve a new `claim_base_sha`, and return the Room to `REWORK`/`READY` on a new control snapshot.

Do not silently rewrite the objective during rework. A material scope change requires Architect/coordinator action and may require dependency-graph/authority revalidation.

## Integration

Accepted output must become durable outside the temporary claim branch before that branch can be deleted. Depending on project policy, integration may be:

- merge/cherry-pick into the Hotel integration ref;
- coordinator materialization/copy of allowlisted output;
- accepted artifact publication into canonical project paths;
- reviewed state/decision update.

The integration method must not bypass project review/owner gates.

## Phase closeout

Before Hotel closure, reviewer/coordinator reconciles all accepted/waived Rooms against canonical source and produces the minimal Hotel history record. That record preserves enough per-Room control/base/accepted-return-head/integration evidence to audit what contract each Room completed without retaining all temporary packets forever.

Only then may temporary Room returns/claim refs become eligible for demolition under retention policy.