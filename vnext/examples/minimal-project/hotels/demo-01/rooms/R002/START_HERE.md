# R002 — Consume accepted R001 output

This Room is intentionally `BLOCKED` in the initial control packet.

Do not claim it until coordinator has:

1. accepted R001 against its pinned control contract;
2. integrated/materialized `source/output-a.md` on the integration line;
3. compiled `input/r001-accepted.md` into R002's control packet;
4. resolved R002 `claim_base_sha` to the integration commit containing accepted source;
5. changed R002 to `READY`, refreshed Reception on `control_ref`, pushed, and verified that remote control commit.

A later Guest fetches that newer control ref, pins its head as `control_commit_sha`, atomically claims R002 from the declared `claim_base_sha`, reads compiled `input/r001-accepted.md` from the control commit and `source/output-a.md` from the claim branch, creates only `source/output-b.md` + return evidence, then ends the session.