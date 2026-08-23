# R001 — Produce first demo output

This entry is part of the Room packet on the Hotel control plane.

Claim this Room only after:

1. fetching `refs/heads/hotel/demo-01/control` and pinning its exact head as `control_commit_sha`;
2. confirming that pinned Reception says Hotel `OPEN` with claims enabled and R001 dependency-ready;
3. confirming fixed ref `hotel/demo-01/claims/R001` is absent;
4. reading this Room manifest from the same pinned control commit and obtaining its exact `claim_base_sha`.

After verified atomic ownership:

1. read `input/brief.md` and `skills/example/SKILL.md` from the pinned `control_commit_sha`;
2. read `source/input.md` from the claim branch initialized at `claim_base_sha`;
3. create only `source/output-a.md` plus this Room's allowlisted return files on the claim branch;
4. record both `control_commit_sha` and `claim_base_sha` in claim/return evidence;
5. record validation truthfully; Python is optional in this example;
6. push the bounded return to the same claim branch and end the Guest session.

Do not load Team Repo, R002, or a newer control packet after claim.