"""File search and preview utilities for Mason Organizer."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from src.core.scanner import categorize_file

TEXT_EXTENSIONS = {".txt", ".md", ".py", ".json", ".csv", ".html", ".css", ".js", ".xml", ".log", ".sh"}


@dataclass
class FileSearchItem:
    path: str
    name: str
    extension: str
    category: str
    size: int


@dataclass
class FileSearchResult:
    folder: Path
    query: str
    matches: list[FileSearchItem] = field(default_factory=list)
    scanned_files: int = 0
    skipped_files: int = 0


def search_files(
    folder: str | Path,
    query: str = "",
    category_filter: str = "All",
    progress_callback: Callable[[int, str], None] | None = None,
) -> FileSearchResult:
    root = Path(folder).expanduser().resolve()
    needle = query.strip().lower()
    result = FileSearchResult(folder=root, query=query.strip())

    files = [path for path in root.rglob("*") if path.is_file()]
    total = len(files)
    if total == 0:
        if progress_callback:
            progress_callback(100, "No files found.")
        return result

    for index, path in enumerate(files, start=1):
        try:
            stat = path.stat()
            category = categorize_file(path)
            name_match = needle in path.name.lower() if needle else True
            category_match = category_filter == "All" or category == category_filter
            if name_match and category_match:
                result.matches.append(
                    FileSearchItem(
                        path=str(path),
                        name=path.name,
                        extension=path.suffix.lower() or "none",
                        category=category,
                        size=stat.st_size,
                    )
                )
            result.scanned_files += 1
        except OSError:
            result.skipped_files += 1

        if progress_callback and (index == total or index % 25 == 0):
            percent = int((index / total) * 100)
            progress_callback(percent, f"Searching {index}/{total} files...")

    result.matches.sort(key=lambda item: (item.category, item.name.lower()))
    if progress_callback:
        progress_callback(100, f"Search complete. Found {len(result.matches)} matches.")
    return result


def preview_file(path: str | Path, max_chars: int = 4000) -> str:
    file_path = Path(path)
    if not file_path.exists() or not file_path.is_file():
        return "Preview unavailable: file does not exist."

    suffix = file_path.suffix.lower()
    try:
        size = file_path.stat().st_size
    except OSError:
        size = 0

    header = [
        f"Name: {file_path.name}",
        f"Path: {file_path}",
        f"Extension: {suffix or 'none'}",
        f"Category: {categorize_file(file_path)}",
        f"Size: {size} bytes",
        "",
    ]

    if suffix not in TEXT_EXTENSIONS:
        header.append("Preview is metadata-only for this file type.")
        return "\n".join(header)

    if size > 2_000_000:
        header.append("Text preview skipped because this file is larger than 2 MB.")
        return "\n".join(header)

    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")[:max_chars]
    except OSError as exc:
        header.append(f"Could not read file: {exc}")
        return "\n".join(header)

    header.append("Preview:")
    header.append("-" * 60)
    header.append(content)
    if len(content) >= max_chars:
        header.append("\n...preview truncated...")
    return "\n".join(header)


def build_search_report(result: FileSearchResult) -> str:
    lines = [
        "Mason Organizer Search Report",
        f"Folder: {result.folder}",
        f"Query: {result.query or '(all files)'}",
        f"Scanned files: {result.scanned_files}",
        f"Matches: {len(result.matches)}",
        f"Skipped files: {result.skipped_files}",
        "",
    ]
    for item in result.matches:
        lines.append(f"[{item.category}] {item.name} — {item.path}")
    return "\n".join(lines)
