"""Local chat helper for Mason Organizer.

This module is intentionally offline/rule-based. It explains app sections and
workflow steps without sending folder details to any external service.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ChatMessage:
    role: str
    content: str


HELP_TOPICS = {
    "dashboard": (
        "Dashboard is the main control center. Use Browse to choose a folder, Scan Folder to inspect it, "
        "Preview Organization to see planned moves, Organize Files to move them safely, and Undo Last Move if needed."
    ),
    "organizer": (
        "Organizer is the focused workspace for file moving. It shows the folder, planned categories, move preview, "
        "safe organizing controls, and undo tools. Always preview first when testing a new folder."
    ),
    "analytics": (
        "Analytics looks for duplicate files and storage waste. It reports possible savings but does not delete files automatically."
    ),
    "search": (
        "Search helps find files by name and category. You can preview safe text files and export a search report."
    ),
    "ai": (
        "AI Assistant is a local helper that summarizes folder scans and recommends cleanup steps. In this version it is rule-based, not cloud AI."
    ),
    "logs": "Logs records activity so users can see what happened during scanning, organizing, searching, and exporting.",
    "settings": "Settings will hold preferences like default folder, theme, safety mode, and future AI options.",
}


def answer_question(question: str) -> str:
    q = question.lower().strip()
    if not q:
        return "Ask me about Dashboard, Organizer, Search, Analytics, AI Assistant, Logs, Settings, or safe workflow."

    if any(word in q for word in ["hello", "hi", "hey"]):
        return "Hey, I’m the Mason Organizer helper. Ask me what a section does, how to organize safely, or what workflow to follow."

    for topic, answer in HELP_TOPICS.items():
        if topic in q:
            return answer

    if any(word in q for word in ["safe", "safely", "workflow", "order", "steps", "work ethic", "productive"]):
        return (
            "Recommended workflow: 1) copy a test folder, 2) scan it, 3) review category counts, "
            "4) preview organization, 5) export/report anything important, 6) organize only after preview, "
            "7) verify the result, and 8) use Undo immediately if something does not look right."
        )

    if any(word in q for word in ["undo", "restore", "move back"]):
        return (
            "Undo uses the latest manifest saved in the logs folder. It moves files back to their original locations when possible. "
            "Use it right after an organize action if the result is not what you expected."
        )

    if any(word in q for word in ["duplicate", "duplicates", "sha", "hash"]):
        return (
            "Duplicate Finder compares files with SHA-256 hashing. Files with the same hash are likely exact duplicates. "
            "Mason Organizer reports them safely and does not delete them automatically."
        )

    if any(word in q for word in ["organize", "category", "categories", "folder"]):
        return (
            "Mason Organizer groups files by extension into categories like Images, Documents, Videos, Audio, Archives, Code, and Other. "
            "Use Preview before Organize so you can check the planned moves first."
        )

    if any(word in q for word in ["ai", "internet", "online", "cloud", "private", "privacy"]):
        return (
            "This assistant is local and rule-based right now. It does not upload your files or send folder data online. "
            "A future version can add optional Ollama/local model support."
        )

    return (
        "I can help explain Mason Organizer sections, safe file-organizing workflow, duplicate reports, undo, search, and AI suggestions. "
        "Try asking: 'How do I use the Organizer?' or 'What is the safest workflow?'"
    )
