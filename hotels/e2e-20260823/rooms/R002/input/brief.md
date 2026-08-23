# Room R002 E2E brief — rework

Read only `source/e2e-input.md`. Produce only the Room write allowlist output plus return evidence.

Return metadata must use the exact pinned `return-vnext-0.1` schema. In particular, `changed_paths` must be full project-relative paths; `allowlist_self_check` uses `result` + `outside_allowlist_paths`; each `checks_run` item uses `command` + `result` + `exit_code`.

Do not read Team Repo, Rin mailbox/log state, unrelated Rooms, or prior attempt audit records.
