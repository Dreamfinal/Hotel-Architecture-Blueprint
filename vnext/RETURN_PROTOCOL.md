# Room Return and Acceptance Protocol

## Guest return

A Room return is delivered on the Room's fixed claim branch. It is not accepted merely because it was pushed.

The return must identify both the immutable Room-contract snapshot and the code base used for implementation. The standard return includes:

```text
hotel_id
room_id
claim_id / session_id
control_ref
control_commit_sha
claim_base_sha
head_sha
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

`control_commit_sha` pins the exact Reception/Room packet/skills/criteria the Guest followed. `claim_base_sha` pins the project code/integration tree from which the working claim branch began.

Valid Guest-requested return statuses are:

- `RETURNED` — implementation/output completed and required available checks were run;
- `IMPLEMENTED_UNVERIFIED` — bounded implementation completed but a declared validation capability was unavailable and this status is allowed by the Room contract;
- `BLOCKED` — objective cannot be completed within current inputs/authority/dependencies.

A Guest must never self-assign `ACCEPTED`.

## Reviewer sequence

The designated reviewer/coordinator:

1. verifies claim branch identity, `control_commit_sha`, `claim_base_sha`, and returned head;
2. reloads the Room contract from the pinned control commit rather than from a newer moving control ref;
3. verifies changed paths against that contract's production + return allowlists and Hotel-wide forbidden paths;
4. checks no forbidden/unrelated path changed;
5. verifies declared deterministic evidence or reruns checks in an authorized runtime;
6. reviews every acceptance criterion from the pinned control packet;
7. checks domain/UX/quality criteria that cannot be reduced to exit codes;
8. records verdict `ACCEPTED`, `REWORK`, or `BLOCKED` with evidence;
9. integrates/materializes accepted output through the Hotel integration path;
10. records the accepted integration/source commit;
11. compiles any dependency output needed by downstream Rooms, resolves newly-ready Room `claim_base_sha` values, and refreshes Room manifests/Reception on `control_ref`;
12. verifies the remote control commit before exposing newly-ready Rooms to Guests.

## Acceptance invariant

```text
push != acceptance
check pass != domain acceptance
acceptance != integration
integration != downstream readiness
integration != Hotel closure
```

Each transition must have explicit evidence.

## Rework

A rework preserves the same Room identity but may create a new control snapshot and/or code base.

The coordinator may preserve/archive the prior attempt, reset the active claim according to `CLAIM_PROTOCOL.md`, update compiled inputs/criteria if necessary, resolve a new `claim_base_sha`, and return the Room to `REWORK`/`READY` on a new `control_commit_sha`.

Do not silently rewrite the objective during rework. A material scope change requires Architect/coordinator action and may require dependency-graph/authority revalidation.

## Integration

Accepted output must become durable outside the temporary claim branch before that branch can be deleted. Depending on project policy, integration may be:

- merge/cherry-pick into the Hotel integration ref;
- coordinator materialization/copy of allowlisted output;
- accepted artifact publication into canonical project paths;
- reviewed state/decision update.

The integration method must not bypass project review/owner gates.

## Phase closeout

Before Hotel closure, reviewer/coordinator reconciles all accepted/waived Rooms against canonical source and produces the minimal Hotel history record. That record should preserve enough accepted control/base/head evidence to audit what contract each Room completed without retaining all temporary packets forever.

Only then may temporary Room returns/claim refs become eligible for demolition under retention policy.