# Hotel Architecture — Agent Entry Point

When the user asks you to "study this architecture", "use the hotel blueprint", or equivalent:

1. Read `START_HERE.md`, `BLUEPRINT.md`, `GIT_PLAYBOOK.md`, and `OPERATING_RULES.md` completely.
2. Inspect the target project and its Git state before proposing rooms. Identify the repository root, remotes, default branch, current branch, worktree state, existing conventions, CI, protected paths, and whether publishing is authorized. Never invent project facts.
3. Design both the work graph and Git graph. Convert the requested outcome into a hotel plan using `templates/HOTEL_MANIFEST.template.json`, `templates/GIT_POLICY.template.json`, and one `ROOM_MANIFEST.json` per room.
4. Keep each room independently understandable: objective, inputs, write allowlist, outputs, checks, reviewer, dependencies, and escalation conditions.
5. Pin a common baseline before parallel work. A room may write only to its allowlist.
6. Use a unique claim for parallel workers. Do not start work until the claim is verified by the coordination mechanism in use.
7. Mechanical checks must be deterministic commands whose exit code decides pass/fail. Human or model judgment belongs to review, not CI.
8. Workers complete work synchronously, produce a room report, and hand off through the declared `next_to` route.
9. Do not merge, deploy, publish, delete, spend money, or make cross-project/policy decisions without explicit authority.
10. If the user only asks you to study the blueprint, explain your understanding and wait. If the user asks you to apply it, create the plan and proceed only within the authority granted.

Before opening a Git-backed hotel, present the user with: baseline ref/SHA, room-to-branch mapping, allowed paths, dependency order, claim mechanism, verification commands, integration strategy, and rollback plan. Never treat commit, push, PR, merge, deploy, or branch deletion as implicitly authorized.

The canonical conceptual source in this package is `BLUEPRINT.md`. Templates are implementation aids and must not override it.
