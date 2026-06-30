"""Analytics utilities for Mason Organizer."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from src.core.scanner import format_size


@dataclass
class DuplicateGroup:
    size: int
    file_hash: str
    files: list[str] = field(default_factory=list)

    @property
    def wasted_space(self) -> int:
        if len(self.files) <= 1:
            return 0
        return self.size * (len(self.files) - 1)


@dataclass
class DuplicateResult:
    folder: Path
    groups: list[DuplicateGroup] = field(default_factory=list)
    scanned_files: int = 0
    skipped_files: int = 0

    @property
    def duplicate_files(self) -> int:
        return sum(max(0, len(group.files) - 1) for group in self.groups)

    @property
    def wasted_space(self) -> int:
        return sum(group.wasted_space for group in self.groups)


def _hash_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        while chunk := file.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def find_duplicates(
    folder: str | Path,
    progress_callback: Callable[[int, str], None] | None = None,
) -> DuplicateResult:
    """Find duplicate files by size first, then SHA-256 hash."""
    root = Path(folder).expanduser().resolve()
    result = DuplicateResult(folder=root)

    size_groups: dict[int, list[Path]] = {}
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        try:
            size = path.stat().st_size
        except OSError:
            result.skipped_files += 1
            continue
        if size == 0:
            continue
        size_groups.setdefault(size, []).append(path)

    candidates = [path for paths in size_groups.values() if len(paths) > 1 for path in paths]
    total = len(candidates)
    if total == 0:
        if progress_callback:
            progress_callback(100, "No duplicate candidates found.")
        return result

    hash_groups: dict[tuple[int, str], list[str]] = {}
    for index, path in enumerate(candidates, start=1):
        try:
            file_hash = _hash_file(path)
            size = path.stat().st_size
            hash_groups.setdefault((size, file_hash), []).append(str(path))
            result.scanned_files += 1
        except OSError:
            result.skipped_files += 1

        if progress_callback and (index == total or index % 5 == 0):
            percent = int((index / total) * 100)
            progress_callback(percent, f"Checking duplicates {index}/{total}...")

    for (size, file_hash), files in hash_groups.items():
        if len(files) > 1:
            result.groups.append(DuplicateGroup(size=size, file_hash=file_hash, files=sorted(files)))

    result.groups.sort(key=lambda group: group.wasted_space, reverse=True)
    if progress_callback:
        progress_callback(100, f"Duplicate scan complete. Potential savings: {format_size(result.wasted_space)}.")
    return result


def build_duplicate_report(result: DuplicateResult) -> str:
    lines = [
        "Mason Organizer Duplicate Report",
        f"Folder: {result.folder}",
        f"Duplicate groups: {len(result.groups)}",
        f"Duplicate files: {result.duplicate_files}",
        f"Potential space savings: {format_size(result.wasted_space)}",
        "",
    ]

    if not result.groups:
        lines.append("No duplicate files found.")
        return "\n".join(lines)

    for number, group in enumerate(result.groups, start=1):
        lines.append(f"Group {number} — {len(group.files)} files — {format_size(group.size)} each")
        lines.append(f"Wasted space: {format_size(group.wasted_space)}")
        for file_path in group.files:
            lines.append(f"  - {file_path}")
        lines.append("")

    return "\n".join(lines)
