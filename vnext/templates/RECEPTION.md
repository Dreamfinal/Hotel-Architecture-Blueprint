# Reception — <HOTEL_ID>

Control ref: `<refs/heads/...>`  
Hotel lifecycle: `<OPEN|...>`  
Claims enabled: `<true|false>`  
Phase objective: `<one short objective>`

## Guest entry

You are a disposable Guest. Do not load Team Repo, permanent Staff memory, the Hotel blueprint, full project history, or unrelated Rooms.

This Reception is valid only when read from the latest remote `control_ref` shown above.

1. Confirm the fetched control ref is the authoritative current ref for this Hotel.
2. Confirm this Hotel is `OPEN` and claims are enabled.
3. Use the claim prefix `<hotel/<hotel-id>/claims/>` for one occupancy lookup.
4. Choose one dependency-ready Room below whose exact fixed claim ref is absent.
5. Claim it atomically from that Room's exact `claim_base_sha` using `CLAIM_PROTOCOL.md` / the repository-local claim instructions.
6. Verify your exact remote ownership.
7. Read only the claimed Room `START_HERE.md`, manifest, declared inputs/skills/source paths.
8. Complete exactly one Room and return through the same claim branch.

## Dependency-ready Rooms

| Room | Objective | Entry |
|---|---|---|
| R001 | <one line> | `rooms/R001/START_HERE.md` |
| R002 | <one line> | `rooms/R002/START_HERE.md` |

## Blocked Rooms

| Room | Blocked by / reason |
|---|---|
| R003 | `R001`, `R002` |

## Occupancy authority

This Reception describes dependency readiness at the control commit you fetched. Remote fixed claim refs are authoritative for live occupancy. Do not edit Reception to claim a Room.

## Stop conditions

Stop without improvising when the control ref is stale/ambiguous, the Hotel is closed, the claim loses a race, ownership cannot be verified, required input/authority is missing, or the Room contract conflicts with project-wide safety.