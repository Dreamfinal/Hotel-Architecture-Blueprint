# Reception — demo-01

Hotel lifecycle: `READY_TO_OPEN`  
Claims enabled: `false`  
Phase objective: demonstrate dependency-aware Room execution.

Claims are not open yet. After validation and the explicit opening control transition, R001 becomes claimable through `hotel/demo-01/claims/R001`.

## Dependency-ready Rooms

| Room | Objective | Entry |
|---|---|---|
| R001 | Produce the first bounded demo output from compiled input. | `rooms/R001/START_HERE.md` |

## Blocked Rooms

| Room | Blocked by / reason |
|---|---|
| R002 | R001 must be ACCEPTED and integrated before its `claim_base_sha` is resolved. |

Do not load Team Repo, permanent Staff memory, the Hotel blueprint, or unrelated Rooms.