# Room Return and Acceptance Protocol

## Guest return

A Room return is delivered on the Room's fixed claim branch. It is not accepted merely because it was pushed.

The Room manifest defines the report path and required fields. The standard return should include:

```text
hotel_id
room_id
claim_id / session_id
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

Valid Guest-requested return statuses are:

- `RETURNED` — implementation/output completed and required available checks were run;
- `IMPLEMENTED_UNVERIFIED` — bounded implementation completed but a declared validation capability was unavailable and this status is allowed by the Room contract;
- `BLOCKED` — objective cannot be completed within current inputs/authority/dependencies.

A Guest must never self-assign `ACCEPTED`.

## Reviewer sequence

The designated reviewer/coordinator:

1. verifies claim branch identity/base/head;
2. verifies changed paths against production + return allowlists;
3. checks no forbidden/unrelated path changed;
4. verifies declared deterministic evidence or reruns checks in an authorized runtime;
5. reviews every acceptance criterion;
6. checks domain/UX/quality criteria that cannot be reduced to exit codes;
7. records verdict `ACCEPTED`, `REWORK`, or `BLOCKED` with evidence;
8. integrates/materializes accepted output through the Hotel integration path;
9. records the accepted integration/source commit;
10. resolves any newly dependency-ready Room `claim_base_sha` and refreshes control state.

## Acceptance invariant

```text
push != acceptance
check pass != domain acceptance
acceptance != integration
integration != Hotel closure
```

Each transition must have explicit evidence.

## Rework

A rework preserves the same Room identity. The coordinator may preserve/archive the prior attempt, reset the active claim according to `CLAIM_PROTOCOL.md`, update compiled inputs/criteria if necessary, and return the Room to `REWORK`/`READY`.

Do not silently rewrite the objective during rework. A material scope change requires Architect/coordinator action and may require dependency graph revalidation.

## Integration

Accepted output must become durable outside the temporary claim branch before that branch can be deleted. Depending on the project, integration may be:

- merge/cherry-pick into the Hotel integration branch;
- coordinator materialization/copy of allowlisted output;
- accepted artifact publication into canonical project paths;
- reviewed state/decision update.

The integration method must not bypass project review/owner gates.

## Phase closeout

Before Hotel closure, reviewer/coordinator reconciles all accepted/waived Rooms against canonical source and produces the minimal Hotel history record. Only then may temporary Room returns be eligible for demolition under retention policy.