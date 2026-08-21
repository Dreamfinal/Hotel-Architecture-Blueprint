# R001 — Produce first demo output

Claim this Room only after the Hotel is `OPEN` and the fixed ref `hotel/demo-01/claims/R001` is absent.

After verified ownership:

1. Read `ROOM_MANIFEST.json`.
2. Read `source/input.md`.
3. Read `skills/example/SKILL.md` from this Room packet.
4. Create only `source/output-a.md` plus files under this Room's `return/` directory.
5. Record validation truthfully; Python is optional in this example.
6. Push the bounded return to the same claim branch and end the Guest session.

Do not load Team Repo or R002.