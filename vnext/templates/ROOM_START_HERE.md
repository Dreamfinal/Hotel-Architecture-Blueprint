# <ROOM_ID> — <ROOM_TITLE>

You own only this Room after a verified atomic claim.

## Objective

<One measurable outcome.>

## Claim identity

- Hotel: `<HOTEL_ID>`
- Room: `<ROOM_ID>`
- Expected base: read `ROOM_MANIFEST.json -> claim_base_sha`
- Claim ref: `hotel/<hotel-id>/claims/<room-id>`

Do not begin implementation until the remote fixed claim ref and claim record verify this session as owner.

## Read exactly this

1. `ROOM_MANIFEST.json`
2. every required path under manifest `inputs`
3. Room-local skill payloads listed under `skills`
4. existing project source paths listed under `source_read_allowlist`

Do not scan the repository or load unrelated Rooms/plans/history.

## Authority

Use only manifest `authority.allowed`. Anything in `authority.forbidden` remains forbidden even if your runtime/tool can perform it.

## Write boundary

Write only `write_allowlist` plus `return_allowlist`. Inputs and source reads are read-only unless also listed for write.

## Validation

Run the manifest checks that are both required and available in this runtime. Record exact commands/results. If a required capability is unavailable, follow the Room return contract; never claim an unrun check passed.

## Acceptance

Satisfy every `acceptance_criteria` item. A successful push is return/delivery evidence only; reviewer/coordinator decides `ACCEPTED`.

## Return

Write the report at `return_contract.report_path` with all `required_fields`, commit/push the bounded result to the same claim branch, verify the remote head, report branch + head commit, then end the Guest session.

## Escalate

Stop and report when any manifest `escalation_conditions` trigger, when a required change is outside write scope, or when project/Room contracts contradict.