#!/usr/bin/env python3
"""Integration-style Git test for Hotel vNext control/base/claim/return validation.

Creates a temporary repository with real SHAs and refs; no network is required.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

VNEXT = Path(__file__).resolve().parents[1]
EXAMPLE = VNEXT / "examples" / "minimal-project"
VALIDATE_HOTEL = VNEXT / "tools" / "validate_hotel.py"
VALIDATE_RETURN = VNEXT / "tools" / "validate_return.py"


def git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=check,
    )


def sha(root: Path, ref: str = "HEAD") -> str:
    return git(root, "rev-parse", ref).stdout.strip()


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run_python(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def expect_ok(label: str, result: subprocess.CompletedProcess[str]) -> None:
    if result.returncode != 0:
        raise AssertionError(f"{label} should pass:\n{result.stdout}")


def expect_fail(label: str, result: subprocess.CompletedProcess[str], needle: str) -> None:
    if result.returncode == 0 or needle not in result.stdout:
        raise AssertionError(f"{label} should fail with {needle!r}:\n{result.stdout}")


def main() -> int:
    with tempfile.TemporaryDirectory() as raw:
        root = Path(raw) / "project"
        shutil.copytree(EXAMPLE, root)

        git(root, "init", "-b", "main")
        git(root, "config", "user.email", "hotel-vnext-test@example.invalid")
        git(root, "config", "user.name", "Hotel vNext Test")
        git(root, "add", "-A")
        git(root, "commit", "-m", "base source and draft hotel packet")
        base_sha = sha(root)

        git(root, "branch", "hotel/demo-01/integration", base_sha)
        git(root, "switch", "-c", "hotel/demo-01/control", base_sha)

        hotel_path = root / "hotels" / "demo-01" / "HOTEL_MANIFEST.json"
        r1_path = root / "hotels" / "demo-01" / "rooms" / "R001" / "ROOM_MANIFEST.json"
        hotel = load(hotel_path)
        hotel["hotel_base_sha"] = base_sha
        hotel["control_ref"] = "refs/heads/hotel/demo-01/control"
        hotel["integration_ref"] = "refs/heads/hotel/demo-01/integration"
        save(hotel_path, hotel)
        r1 = load(r1_path)
        r1["claim_base_sha"] = base_sha
        save(r1_path, r1)
        git(root, "add", "-A")
        git(root, "commit", "-m", "resolve control packet against real base")
        control_sha = sha(root)

        opening = run_python(
            VALIDATE_HOTEL,
            str(root / "hotels" / "demo-01"),
            "--project-root",
            str(root),
            "--check-git-refs",
        )
        expect_ok("Git opening validation", opening)

        git(root, "switch", "main")
        wrong_control = run_python(
            VALIDATE_HOTEL,
            str(root / "hotels" / "demo-01"),
            "--project-root",
            str(root),
            "--check-git-refs",
        )
        expect_fail("opening from stale/non-control checkout", wrong_control, "is not current control_ref head")

        git(root, "switch", "-c", "hotel/demo-01/claims/R001", base_sha)
        return_dir = root / "hotels" / "demo-01" / "rooms" / "R001" / "return"
        claim_path = return_dir / "CLAIM.json"
        claim = {
            "schema_version": "claim-vnext-0.1",
            "hotel_id": "demo-01",
            "room_id": "R001",
            "claim_id": "git-flow-claim-r001",
            "session_id": "git-flow-session-r001",
            "claimed_at_utc": "2026-08-21T09:00:00Z",
            "control_ref": "refs/heads/hotel/demo-01/control",
            "control_commit_sha": control_sha,
            "claim_base_sha": base_sha,
            "status": "CLAIMED",
            "head_sha": None,
        }
        save(claim_path, claim)
        git(root, "add", str(claim_path.relative_to(root)))
        git(root, "commit", "-m", "claim R001")

        output_path = root / "source" / "output-a.md"
        output_path.write_text("# Accepted candidate output A\n", encoding="utf-8")
        git(root, "add", str(output_path.relative_to(root)))
        git(root, "commit", "-m", "implement R001")
        implementation_sha = sha(root)

        return_path = return_dir / "ROOM_RETURN.json"
        returned = {
            "schema_version": "return-vnext-0.1",
            "hotel_id": "demo-01",
            "room_id": "R001",
            "claim_id": claim["claim_id"],
            "session_id": claim["session_id"],
            "control_ref": claim["control_ref"],
            "control_commit_sha": control_sha,
            "claim_base_sha": base_sha,
            "implementation_commit_sha": implementation_sha,
            "status": "RETURNED",
            "changed_paths": [
                "hotels/demo-01/rooms/R001/return/CLAIM.json",
                "hotels/demo-01/rooms/R001/return/ROOM_RETURN.json",
                "source/output-a.md",
            ],
            "allowlist_self_check": {"result": "PASS", "outside_allowlist_paths": []},
            "implemented_contract": ["Created output A from declared inputs."],
            "checks_run": [
                {
                    "id": "output-exists",
                    "command": "python -c test-output-exists",
                    "result": "PASS",
                    "exit_code": 0,
                    "evidence": "test fixture",
                }
            ],
            "checks_unrun": [],
            "output_paths": ["source/output-a.md"],
            "unresolved": [],
            "requested_next_state": "REVIEW",
            "notes": "Integration test return; final returned head is reviewer-derived.",
        }
        save(return_path, returned)
        git(root, "add", str(return_path.relative_to(root)))
        git(root, "commit", "-m", "return R001")
        return_head = sha(root)

        returned_ok = run_python(
            VALIDATE_RETURN,
            str(root),
            "--hotel-id",
            "demo-01",
            "--room-id",
            "R001",
            "--return-ref",
            "refs/heads/hotel/demo-01/claims/R001",
        )
        expect_ok("returned Room Git validation", returned_ok)
        if return_head not in returned_ok.stdout:
            raise AssertionError(f"reviewer-derived return_head_sha missing:\n{returned_ok.stdout}")

        current_state = root / "CURRENT_STATE.md"
        current_state.write_text(current_state.read_text(encoding="utf-8") + "\nforbidden mutation\n", encoding="utf-8")
        returned["changed_paths"].append("CURRENT_STATE.md")
        save(return_path, returned)
        git(root, "add", "CURRENT_STATE.md", str(return_path.relative_to(root)))
        git(root, "commit", "-m", "invalid forbidden mutation")
        forbidden = run_python(
            VALIDATE_RETURN,
            str(root),
            "--hotel-id",
            "demo-01",
            "--room-id",
            "R001",
            "--return-ref",
            "refs/heads/hotel/demo-01/claims/R001",
        )
        expect_fail("review catches forbidden returned mutation", forbidden, "Hotel forbidden write path")

    print("GIT_FLOW_TESTS_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
