#!/usr/bin/env python3
"""Black-box tests for validate_hotel.py using only the Python standard library."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

VNEXT = Path(__file__).resolve().parents[1]
VALIDATOR = VNEXT / "tools" / "validate_hotel.py"
EXAMPLE = VNEXT / "examples" / "minimal-project"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run(project: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(VALIDATOR),
            str(project / "hotels" / "demo-01"),
            "--project-root",
            str(project),
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def copied_project(temp: Path) -> Path:
    target = temp / "project"
    shutil.copytree(EXAMPLE, target)
    return target


def expect_ok(label: str, project: Path) -> None:
    result = run(project)
    if result.returncode != 0:
        raise AssertionError(f"{label} should pass, got:\n{result.stdout}")


def expect_fail(label: str, project: Path, needle: str) -> None:
    result = run(project)
    if result.returncode == 0:
        raise AssertionError(f"{label} should fail, got:\n{result.stdout}")
    if needle not in result.stdout:
        raise AssertionError(f"{label} missing expected error {needle!r}:\n{result.stdout}")


def main() -> int:
    with tempfile.TemporaryDirectory() as raw:
        temp = Path(raw)

        project = copied_project(temp / "case-pass")
        expect_ok("minimal dependency Hotel", project)

        project = copied_project(temp / "case-missing-source")
        (project / "source" / "input.md").unlink()
        expect_fail("claimable missing source", project, "source path missing at claimable state")

        project = copied_project(temp / "case-missing-packet-input")
        (project / "hotels" / "demo-01" / "rooms" / "R001" / "input" / "brief.md").unlink()
        expect_fail("claimable missing compiled input", project, "required compiled input missing at claimable state")

        project = copied_project(temp / "case-traversal")
        r1_path = project / "hotels" / "demo-01" / "rooms" / "R001" / "ROOM_MANIFEST.json"
        r1 = load(r1_path)
        r1["write_allowlist"] = ["../outside.md"]
        save(r1_path, r1)
        expect_fail("path traversal", project, "unsafe path segments")

        project = copied_project(temp / "case-forbidden")
        r1_path = project / "hotels" / "demo-01" / "rooms" / "R001" / "ROOM_MANIFEST.json"
        r1 = load(r1_path)
        r1["write_allowlist"] = ["CURRENT_STATE.md"]
        save(r1_path, r1)
        expect_fail("Hotel-wide forbidden write", project, "overlaps Hotel forbidden write path")

        project = copied_project(temp / "case-cycle")
        r1_path = project / "hotels" / "demo-01" / "rooms" / "R001" / "ROOM_MANIFEST.json"
        r1 = load(r1_path)
        r1["depends_on"] = ["R002"]
        save(r1_path, r1)
        hotel_path = project / "hotels" / "demo-01" / "HOTEL_MANIFEST.json"
        hotel = load(hotel_path)
        hotel["dependency_edges"].append({"from": "R002", "to": "R001"})
        save(hotel_path, hotel)
        expect_fail("dependency cycle", project, "dependency graph contains a cycle")

        project = copied_project(temp / "case-overlap")
        hotel_path = project / "hotels" / "demo-01" / "HOTEL_MANIFEST.json"
        hotel = load(hotel_path)
        hotel["dependency_edges"] = []
        save(hotel_path, hotel)
        r2_path = project / "hotels" / "demo-01" / "rooms" / "R002" / "ROOM_MANIFEST.json"
        r2 = load(r2_path)
        r2["logical_state"] = "READY"
        r2["depends_on"] = []
        r2["claim_base_sha"] = "b" * 40
        r2["inputs"] = []
        r2["source_read_allowlist"] = ["source/input.md"]
        r2["write_allowlist"] = ["source/output-a.md"]
        save(r2_path, r2)
        expect_fail("simultaneous write overlap", project, "overlap writes")

    print("VALIDATOR_TESTS_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
