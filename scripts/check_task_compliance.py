from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "erp-blueprint/docs/backlog/task-registry.yaml"


def load_registry_text() -> str:
    if not REGISTRY.exists():
        raise SystemExit(f"Task registry not found: {REGISTRY}")
    return REGISTRY.read_text(encoding="utf-8")


def check_task(task_id: str) -> list[str]:
    registry = load_registry_text()
    marker = f"- id: {task_id}"
    if marker not in registry:
        return [f"{task_id}: task is not registered."]

    errors: list[str] = []
    required_fields = [
        "title",
        "epic",
        "module",
        "status",
        "dependencies",
        "documentation",
        "academy",
        "tests",
        "review_status",
    ]
    task_block = registry.split(marker, 1)[1].split("\n  - id:", 1)[0]
    for field in required_fields:
        if f"    {field}:" not in task_block:
            errors.append(f"{task_id}: missing field {field}.")

    valid_statuses = {"planned", "ready", "in_progress", "review", "completed", "blocked"}
    status_line = next(
        (line for line in task_block.splitlines() if line.strip().startswith("status:")),
        "",
    )
    status = status_line.split(":", 1)[1].strip() if ":" in status_line else ""
    if status not in valid_statuses:
        errors.append(f"{task_id}: invalid status.")

    for line in task_block.splitlines():
        stripped = line.strip()
        if stripped.startswith("- docs/") or stripped.startswith("- erp-platform/"):
            path = stripped.removeprefix("- ").strip()
            if not (ROOT / path).exists():
                errors.append(f"{task_id}: documentation not found: {path}.")
        if stripped.startswith("- erp-blueprint/docs/academy/"):
            path = stripped.removeprefix("- ").strip()
            if not (ROOT / path).exists():
                errors.append(f"{task_id}: academy not found: {path}.")

    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    if task_id not in changelog:
        errors.append(f"{task_id}: CHANGELOG does not mention task.")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", required=True)
    args = parser.parse_args()
    errors = check_task(args.task)
    if errors:
        for error in errors:
            print(error)
        return 1
    print(f"{args.task}: compliance OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
