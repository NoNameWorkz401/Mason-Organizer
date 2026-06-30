"""Folder scanning utilities for Mason Organizer."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

CATEGORY_EXTENSIONS = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp", ".tiff"},
    "Documents": {".pdf", ".docx", ".doc", ".txt", ".rtf", ".odt", ".md"},
    "Spreadsheets": {".xlsx", ".xls", ".csv", ".ods"},
    "Presentations": {".pptx", ".ppt", ".odp"},
    "Videos": {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v"},
    "Audio": {".mp3", ".wav", ".aac", ".flac", ".m4a", ".ogg"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz"},
    "Code": {".py", ".js", ".html", ".css", ".json", ".xml", ".sh", ".java", ".cpp", ".c"},
}


def categorize_file(path: Path) -> str:
    suffix = path.suffix.lower()
    for category, extensions in CATEGORY_EXTENSIONS.items():
        if suffix in extensions:
            return category
    return "Other"


@dataclass
class ScanResult:
    folder: Path
    total_files: int = 0
    total_folders: int = 0
    total_size: int = 0
    categories: dict[str, int] = field(default_factory=dict)
    largest_files: list[tuple[str, int]] = field(default_factory=list)

    @property
    def total_size_mb(self) -> float:
        return self.total_size / (1024 * 1024)


def format_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.1f} KB"
    if size_bytes < 1024 ** 3:
        return f"{size_bytes / (1024 ** 2):.1f} MB"
    return f"{size_bytes / (1024 ** 3):.2f} GB"


def scan_folder(
    folder: str | Path,
    progress_callback: Callable[[int, str], None] | None = None,
) -> ScanResult:
    root = Path(folder).expanduser().resolve()
    result = ScanResult(folder=root)

    files: list[Path] = []
    for item in root.rglob("*"):
        if item.is_dir():
            result.total_folders += 1
        elif item.is_file():
            files.append(item)

    total = len(files)
    if total == 0:
        if progress_callback:
            progress_callback(100, "No files found.")
        return result

    largest: list[tuple[str, int]] = []

    for index, file_path in enumerate(files, start=1):
        try:
            size = file_path.stat().st_size
        except OSError:
            size = 0

        category = categorize_file(file_path)
        result.categories[category] = result.categories.get(category, 0) + 1
        result.total_files += 1
        result.total_size += size
        largest.append((str(file_path), size))

        if progress_callback and (index == total or index % 10 == 0):
            percent = int((index / total) * 100)
            progress_callback(percent, f"Scanning {index}/{total} files...")

    result.largest_files = sorted(largest, key=lambda item: item[1], reverse=True)[:5]
    if progress_callback:
        progress_callback(100, "Scan complete.")
    return result
