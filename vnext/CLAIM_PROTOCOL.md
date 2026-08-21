# Atomic Claim Protocol

## 1. Claim primitive

Each Room has one fixed remote claim branch:

```text
hotel/<hotel-id>/claims/<room-id>
```

Branch existence is the occupancy lock. The branch must be created from the Room's exact `claim_base_sha` using a non-force atomic ref creation. GitHub `create ref/branch` or a normal non-force `git push <sha>:refs/heads/<claim-ref>` are equivalent implementations.

If the ref already exists, the claim fails. The losing Guest must not modify/delete/force the winner's branch.

## 2. Why the fixed ref is atomic

Guests do not claim by writing a shared lobby file or by observing that a room “looks vacant.” Two concurrent Guests may both observe vacancy, but only one remote ref creation can succeed at the fixed Room claim name.

The claim ref is also the Room working/return branch, so no second coordination system is required.

## 3. Claim sequence

A Guest:

1. reads `RECEPTION.md` and Room ID candidates;
2. reads only the allowed claim prefix occupancy listing;
3. selects a dependency-ready Room whose exact claim ref is absent;
4. reads its `ROOM_MANIFEST.json` and exact `claim_base_sha` only as required for the claim;
5. creates `hotel/<hotel-id>/claims/<room-id>` from that SHA without force;
6. writes `hotels/<hotel-id>/rooms/<room-id>/return/CLAIM.json` on the claim branch with:
   - `hotel_id`;
   - `room_id`;
   - stable `session_id` / `claim_id`;
   - `claimed_at_utc`;
   - `claim_base_sha`;
   - `status: CLAIMED`;
7. commits/pushes the claim record to the same branch;
8. fetches/reads the exact remote claim record and branch head;
9. proceeds only if Hotel/Room/session/base all match.

A runtime that cannot immediately write the claim record may still treat successful fixed-ref creation as provisional ownership, but it must verify the exact remote ref before modifying production paths and must create the claim record before return.

## 4. Claim scope

One ordinary Guest session owns one Room. The Guest may not probe individual foreign Room branches, modify a winner's claim, delete claim refs, or claim a second Room after completing the first.

## 5. Return on the claim branch

The Guest commits all allowed implementation/output and return evidence to the same claim branch. The final Room return records:

```text
status: RETURNED | IMPLEMENTED_UNVERIFIED | BLOCKED
claim_base_sha: ...
head_sha: ...
changed_paths: ...
checks_run: ...
checks_unrun: ...
unresolved: ...
```

Only reviewer/coordinator action can transition durable Room state to `ACCEPTED`.

## 6. Dependency-aware bases

The Hotel has immutable `hotel_base_sha`, but every Room has its own `claim_base_sha`.

- Independent Room: usually `claim_base_sha == hotel_base_sha` or the pinned integration tip at opening.
- Dependent Room: `claim_base_sha` is resolved only after all dependencies are `ACCEPTED` and their required output is integrated/materialized.

A Room with unresolved `claim_base_sha` is not claimable.

## 7. Stale claim detection

Staleness is policy, not a background runtime requirement. `HOTEL_MANIFEST.json` may define `claim_stale_after_hours`. A claim can be considered for recovery only when:

- it has exceeded that threshold or the owner explicitly declares it abandoned;
- no accepted integration references its unreviewed tip;
- there is no credible active Guest continuation;
- coordinator/housekeeping has authority to recover it.

No ordinary Guest may reclaim/delete a stale-looking branch itself.

## 8. Recovery procedure

Coordinator/housekeeping performs recovery as a controlled sequence:

1. fetch/read exact claim branch and return evidence;
2. write a recovery audit note containing previous claim/session/head and reason;
3. preserve the stale tip under an immutable/restricted audit ref such as:
   `refs/archive/hotel/<hotel-id>/<room-id>/attempt-<n>`;
4. verify the archive ref points to the expected stale tip;
5. delete the fixed active claim branch under explicit recovery authority;
6. reset the Room logical state to `READY` or `REWORK` with a new/resolved `claim_base_sha` if appropriate;
7. refresh Reception/control state;
8. a later fresh Guest may atomically create the fixed claim ref again.

This keeps attempt history without making every Guest carry old attempts in context.

## 9. Acceptance and claim cleanup

After a Room is accepted/integrated, its claim branch may remain until Hotel closure for audit or may be archived earlier according to retention policy. Deletion must never be the only copy of an accepted output: accepted source/integration commit and required evidence must already be durable.

At Hotel demolition, temporary claim refs are removed only after closure/retention gates pass.