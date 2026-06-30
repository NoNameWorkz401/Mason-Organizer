"""Local AI-style assistant utilities for Mason Organizer.

This module does not call any cloud AI service. It uses deterministic rules to
produce helpful cleanup suggestions from a folder scan. A future release can add
optional Ollama/OpenAI integration on top of this same interface.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from src.core.scanner import ScanResult, format_size, scan_folder


@dataclass
class AssistantInsight:
    title: str
    detail: str


@dataclass
class AssistantReport:
    folder: Path
    scan: ScanResult
    summary: str
    insights: list[AssistantInsight] = field(default_factory=list)
    suggested_actions: list[str] = field(default_factory=list)
    suggested_structure: dict[str, list[str]] = field(default_factory=dict)


def _dominant_category(scan: ScanResult) -> tuple[str, int] | None:
    if not scan.categories:
        return None
    return max(scan.categories.items(), key=lambda item: item[1])


def _category_summary(scan: ScanResult) -> str:
    if not scan.categories:
        return "No category data available."
    parts = [f"{category}: {count}" for category, count in sorted(scan.categories.items(), key=lambda item: item[0])]
    return ", ".join(parts)


def build_assistant_report(folder: str | Path, progress_callback=None) -> AssistantReport:
    scan = scan_folder(folder, progress_callback)
    dominant = _dominant_category(scan)

    if scan.total_files == 0:
        summary = "This folder does not contain files Mason Organizer can scan yet."
    elif dominant:
        category, count = dominant
        percent = round((count / scan.total_files) * 100)
        summary = (
            f"I scanned {scan.total_files} files across {scan.total_folders} folders. "
            f"The folder is mostly {category.lower()} files ({count} files, about {percent}% of the folder). "
            f"Total scanned size is {format_size(scan.total_size)}."
        )
    else:
        summary = f"I scanned {scan.total_files} files totaling {format_size(scan.total_size)}."

    insights: list[AssistantInsight] = []
    actions: list[str] = []

    if scan.total_files == 0:
        insights.append(AssistantInsight("Empty scan", "No files were found in the selected folder."))
        actions.append("Choose a folder that contains files, then run the assistant again.")
        return AssistantReport(Path(folder), scan, summary, insights, actions, {})

    insights.append(AssistantInsight("Category mix", _category_summary(scan)))

    if scan.total_folders > scan.total_files and scan.total_files > 0:
        insights.append(
            AssistantInsight(
                "Folder-heavy structure",
                "There are more folders than files. This may mean the folder has old empty folders or deeply nested organization.",
            )
        )
        actions.append("Use Analytics in a future cleanup pass to look for empty or duplicate-heavy areas.")

    if dominant:
        category, count = dominant
        if count >= max(5, scan.total_files * 0.5):
            actions.append(f"Start by organizing {category} first because it is the largest category in this folder.")
        else:
            actions.append("Use Preview Organization first because this folder has a mixed file set.")

    if scan.total_size > 1024**3:
        insights.append(AssistantInsight("Large folder", f"This folder is larger than 1 GB at {format_size(scan.total_size)}."))
        actions.append("Run Duplicate Finder before organizing to avoid moving unnecessary copies around.")

    if scan.largest_files:
        largest_name, largest_size = scan.largest_files[0]
        insights.append(AssistantInsight("Largest file", f"{Path(largest_name).name} is the largest file at {format_size(largest_size)}."))

    if scan.categories.get("Archives", 0) >= 3:
        actions.append("Review archive files manually before moving them; ZIP/RAR files often contain mixed project content.")
    if scan.categories.get("Code", 0) >= 3:
        actions.append("Be careful organizing code folders automatically; project files should usually stay together.")
    if scan.categories.get("Images", 0) >= 10:
        actions.append("Images may benefit from a later photo workflow: screenshots, mockups, logos, and product photos.")

    actions.append("Use Preview Organization before Organize Files so you can review the planned moves safely.")

    structure = {
        "Images": ["Screenshots", "Product Mockups", "Logos", "Other Images"],
        "Documents": ["PDFs", "Word Docs", "Notes", "Business Docs"],
        "Media": ["Videos", "Audio"],
        "Projects": ["Code", "Design Files", "Archives"],
        "Other": ["Review Manually"],
    }

    return AssistantReport(Path(folder), scan, summary, insights, actions, structure)


def export_assistant_report(report: AssistantReport) -> str:
    lines = [
        "Mason Organizer AI Assistant Report",
        "=" * 40,
        f"Folder: {report.folder}",
        f"Files: {report.scan.total_files}",
        f"Folders: {report.scan.total_folders}",
        f"Size: {format_size(report.scan.total_size)}",
        "",
        "Summary",
        "-------",
        report.summary,
        "",
        "Insights",
        "--------",
    ]
    for insight in report.insights:
        lines.append(f"- {insight.title}: {insight.detail}")
    lines += ["", "Suggested Actions", "-----------------"]
    for action in report.suggested_actions:
        lines.append(f"- {action}")
    lines += ["", "Suggested Structure", "-------------------"]
    for top, children in report.suggested_structure.items():
        lines.append(f"{top}/")
        for child in children:
            lines.append(f"  - {child}/")
    return "\n".join(lines)
