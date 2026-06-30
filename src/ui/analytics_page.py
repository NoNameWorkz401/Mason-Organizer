from __future__ import annotations

import queue
import threading
from datetime import datetime
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk

from src.core.analytics import DuplicateResult, build_duplicate_report, find_duplicates
from src.core.scanner import format_size
from src.ui.theme import COLORS


class AnalyticsPage(ctk.CTkFrame):
    def __init__(self, parent, set_status, add_log):
        super().__init__(parent, corner_radius=22, fg_color=COLORS["background"])
        self.set_status = set_status
        self.add_log = add_log
        self.selected_folder = ctk.StringVar(value="No folder selected")
        self.result: DuplicateResult | None = None
        self.queue: queue.Queue = queue.Queue()

        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure(4, weight=1)

        ctk.CTkLabel(self, text="Analytics", font=ctk.CTkFont(size=32, weight="bold"), text_color=COLORS["text"]).grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 6)
        )
        ctk.CTkLabel(
            self,
            text="Find duplicate files and review cleanup opportunities before deleting anything manually.",
            font=ctk.CTkFont(size=15),
            text_color=COLORS["muted"],
        ).grid(row=1, column=0, columnspan=3, sticky="w", pady=(0, 18))

        folder_box = ctk.CTkFrame(self, corner_radius=18, fg_color=COLORS["surface"])
        folder_box.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(0, 18))
        folder_box.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(folder_box, textvariable=self.selected_folder, anchor="w", text_color=COLORS["text"]).grid(
            row=0, column=0, padx=18, pady=16, sticky="ew"
        )
        ctk.CTkButton(folder_box, text="Browse", width=120, height=40, command=self.select_folder).grid(
            row=0, column=1, padx=18, pady=16
        )

        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(0, 18))
        self.scan_button = ctk.CTkButton(actions, text="Find Duplicates", height=42, corner_radius=12, command=self.start_duplicate_scan)
        self.scan_button.grid(row=0, column=0, padx=(0, 12))
        self.export_button = ctk.CTkButton(
            actions,
            text="Export Report",
            height=42,
            corner_radius=12,
            fg_color=COLORS["surface_light"],
            hover_color=COLORS["surface_lighter"],
            command=self.export_report,
        )
        self.export_button.grid(row=0, column=1, padx=12)

        summary = ctk.CTkFrame(self, corner_radius=18, fg_color=COLORS["surface"])
        summary.grid(row=4, column=0, columnspan=3, sticky="nsew")
        summary.grid_columnconfigure(0, weight=1)
        summary.grid_rowconfigure(2, weight=1)

        self.progress_label = ctk.CTkLabel(summary, text="Progress: 0%", text_color=COLORS["muted"], anchor="w")
        self.progress_label.grid(row=0, column=0, padx=18, pady=(16, 4), sticky="ew")
        self.progress = ctk.CTkProgressBar(summary, height=14, corner_radius=8)
        self.progress.grid(row=1, column=0, padx=18, pady=(0, 16), sticky="ew")
        self.progress.set(0)

        self.output = ctk.CTkTextbox(summary, fg_color=COLORS["surface_light"], text_color=COLORS["text"], corner_radius=14)
        self.output.grid(row=2, column=0, padx=18, pady=(0, 18), sticky="nsew")
        self._set_output("Choose a folder and run Find Duplicates. Mason Organizer does not delete duplicate files automatically.")

    def _set_output(self, text: str) -> None:
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.insert("1.0", text)
        self.output.configure(state="disabled")

    def select_folder(self) -> None:
        folder = filedialog.askdirectory()
        if folder:
            self.selected_folder.set(folder)
            self.set_status("Analytics folder selected")
            self.add_log(f"Analytics folder selected: {folder}")

    def start_duplicate_scan(self) -> None:
        folder = self.selected_folder.get()
        if folder == "No folder selected" or not Path(folder).exists():
            self.set_status("Choose a folder first")
            self.add_log("Duplicate scan cancelled: no valid folder selected.")
            return

        self.scan_button.configure(state="disabled", text="Scanning...")
        self.progress.set(0)
        self.progress_label.configure(text="Progress: 0%")
        self.set_status("Finding duplicates")
        self.add_log("Started duplicate scan...")

        thread = threading.Thread(target=self._worker, args=(folder,), daemon=True)
        thread.start()
        self.after(100, self._process_queue)

    def _worker(self, folder: str) -> None:
        def progress(percent: int, message: str) -> None:
            self.queue.put(("progress", percent, message))

        try:
            result = find_duplicates(folder, progress)
            self.queue.put(("done", result))
        except Exception as exc:  # Keeps the UI alive during user-facing file scans.
            self.queue.put(("error", str(exc)))

    def _process_queue(self) -> None:
        try:
            while True:
                message = self.queue.get_nowait()
                if message[0] == "progress":
                    _, percent, text = message
                    self.progress.set(percent / 100)
                    self.progress_label.configure(text=f"Progress: {percent}%")
                    self.set_status(text)
                elif message[0] == "done":
                    _, result = message
                    self._show_result(result)
                    self.scan_button.configure(state="normal", text="Find Duplicates")
                    return
                elif message[0] == "error":
                    _, error = message
                    self.set_status("Duplicate scan failed")
                    self.add_log(f"Duplicate scan error: {error}")
                    self.scan_button.configure(state="normal", text="Find Duplicates")
                    return
        except queue.Empty:
            pass
        self.after(100, self._process_queue)

    def _show_result(self, result: DuplicateResult) -> None:
        self.result = result
        self.progress.set(1)
        self.progress_label.configure(text="Progress: 100%")
        self.set_status("Duplicate scan complete")
        self.add_log(
            f"Duplicate scan complete: {len(result.groups)} groups, {result.duplicate_files} duplicate files, {format_size(result.wasted_space)} potential savings."
        )

        if not result.groups:
            self._set_output("No duplicate files found. Nice clean folder.")
            return

        lines = [
            f"Duplicate groups: {len(result.groups)}",
            f"Duplicate files: {result.duplicate_files}",
            f"Potential space savings: {format_size(result.wasted_space)}",
            "",
            "Largest duplicate groups:",
        ]
        for group in result.groups[:10]:
            lines.append(f"\n{len(group.files)} files — {format_size(group.size)} each — saves {format_size(group.wasted_space)}")
            for file_path in group.files[:4]:
                lines.append(f"  • {Path(file_path).name}")
            if len(group.files) > 4:
                lines.append(f"  • ...and {len(group.files) - 4} more")
        self._set_output("\n".join(lines))

    def export_report(self) -> None:
        if self.result is None:
            self.set_status("No duplicate report to export")
            self.add_log("Export cancelled: run a duplicate scan first.")
            return

        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        report_path = logs_dir / f"duplicate_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        report_path.write_text(build_duplicate_report(self.result), encoding="utf-8")
        self.set_status("Duplicate report exported")
        self.add_log(f"Duplicate report exported: {report_path}")
