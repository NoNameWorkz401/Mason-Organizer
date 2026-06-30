"""Safe file organization utilities for Mason Organizer."""

from __future__ import annotations

import json
import shutil
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable

from src.core.scanner import categorize_file

CATEGORY_FOLDER_NAMES = {
    "Images": "Images",
    "Documents": "Documents",
    "Spreadsheets": "Spreadsheets",
    "Presentations": "Presentations",
    "Videos": "Videos",
    "Audio": "Audio",
    "Archives": "Archives",
    "Code": "Code",
    "Other": "Other",
}

PROTECTED_FOLDER_NAMES = set(CATEGORY_FOLDER_NAMES.values()) | {"logs", ".venv", "venv", "env", "__pycache__"}


@dataclass
class PlannedMove:
    source: str
    destination: str
    category: str
    size: int = 0


@dataclass
class OrganizationPlan:
    root: str
    created_at: str
    moves: list[PlannedMove] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)

    @property
    def total_files(self) -> int:
        return len(self.moves)

    @property
    def categories(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for move in self.moves:
            counts[move.category] = counts.get(move.category, 0) + 1
        return counts


@dataclass
class OrganizationResult:
    moved_files: int = 0
    skipped_files: int = 0
    manifest_path: str | None = None
    errors: list[str] = field(default_factory=list)


def _is_inside_protected_folder(file_path: Path, root: Path) -> bool:
    try:
        relative_parts = file_path.relative_to(root).parts[:-1]
    except ValueError:
        return True
    return any(part in PROTECTED_FOLDER_NAMES for part in relative_parts)


def _unique_destination(destination: Path) -> Path:
    if not destination.exists():
        return destination

    stem = destination.stem
    suffix = destination.suffix
    parent = destination.parent
    counter = 1

    while True:
        candidate = parent / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def build_organization_plan(folder: str | Path) -> OrganizationPlan:
    root = Path(folder).expanduser().resolve()
    plan = OrganizationPlan(root=str(root), created_at=datetime.now().isoformat(timespec="seconds"))

    if not root.exists() or not root.is_dir():
        plan.skipped.append(f"Invalid folder: {root}")
        return plan

    for file_path in root.rglob("*"):
        if not file_path.is_file():
            continue

        if _is_inside_protected_folder(file_path, root):
            plan.skipped.append(str(file_path))
            continue

        category = categorize_file(file_path)
        destination_folder = root / CATEGORY_FOLDER_NAMES.get(category, "Other")
        destination = _unique_destination(destination_folder / file_path.name)

        # If the file is already where it belongs, skip it.
        if file_path.resolve() == destination.resolve():
            plan.skipped.append(str(file_path))
            continue

        try:
            size = file_path.stat().st_size
        except OSError:
            size = 0

        plan.moves.append(
            PlannedMove(
                source=str(file_path),
                destination=str(destination),
                category=category,
                size=size,
            )
        )

    return plan


def save_manifest(plan: OrganizationPlan, logs_folder: str | Path = "logs") -> Path:
    log_dir = Path(logs_folder)
    log_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = log_dir / f"undo_manifest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    data = {
        "root": plan.root,
        "created_at": plan.created_at,
        "moves": [asdict(move) for move in plan.moves],
        "skipped": plan.skipped,
    }
    manifest_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    (log_dir / "undo_manifest_latest.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    return manifest_path


def execute_plan(
    plan: OrganizationPlan,
    progress_callback: Callable[[int, str], None] | None = None,
    logs_folder: str | Path = "logs",
) -> OrganizationResult:
    result = OrganizationResult(skipped_files=len(plan.skipped))
    total = len(plan.moves)

    if total == 0:
        if progress_callback:
            progress_callback(100, "No files to organize.")
        return result

    for index, move in enumerate(plan.moves, start=1):
        source = Path(move.source)
        destination = Path(move.destination)

        try:
            if not source.exists():
                result.skipped_files += 1
                continue
            destination.parent.mkdir(parents=True, exist_ok=True)
            final_destination = _unique_destination(destination)
            shutil.move(str(source), str(final_destination))
            move.destination = str(final_destination)
            result.moved_files += 1
        except Exception as exc:  # noqa: BLE001 - user-facing file operation should continue safely.
            result.errors.append(f"{source.name}: {exc}")

        if progress_callback and (index == total or index % 5 == 0):
            percent = int((index / total) * 100)
            progress_callback(percent, f"Organizing {index}/{total} files...")

    if result.moved_files:
        result.manifest_path = str(save_manifest(plan, logs_folder))

    if progress_callback:
        progress_callback(100, "Organization complete.")

    return result


def undo_last_organization(
    manifest_path: str | Path = "logs/undo_manifest_latest.json",
    progress_callback: Callable[[int, str], None] | None = None,
) -> OrganizationResult:
    manifest = Path(manifest_path)
    result = OrganizationResult()

    if not manifest.exists():
        result.errors.append("No undo manifest found.")
        return result

    data = json.loads(manifest.read_text(encoding="utf-8"))
    moves = data.get("moves", [])
    total = len(moves)

    for index, move in enumerate(reversed(moves), start=1):
        source = Path(move["destination"])
        destination = Path(move["source"])

        try:
            if not source.exists():
                result.skipped_files += 1
                continue
            destination.parent.mkdir(parents=True, exist_ok=True)
            final_destination = _unique_destination(destination)
            shutil.move(str(source), str(final_destination))
            result.moved_files += 1
        except Exception as exc:  # noqa: BLE001
            result.errors.append(f"{source.name}: {exc}")

        if progress_callback and total and (index == total or index % 5 == 0):
            percent = int((index / total) * 100)
            progress_callback(percent, f"Undoing {index}/{total} files...")

    if progress_callback:
        progress_callback(100, "Undo complete.")

    return result
