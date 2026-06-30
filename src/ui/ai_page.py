from __future__ import annotations

import queue
import threading
from datetime import datetime
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk

from src.core.ai_assistant import AssistantReport, build_assistant_report, export_assistant_report
from src.core.scanner import format_size
from src.ui.theme import COLORS


class AIAssistantPage(ctk.CTkFrame):
    def __init__(self, parent, set_status, add_log):
        super().__init__(parent, corner_radius=22, fg_color=COLORS["background"])
        self.set_status = set_status
        self.add_log = add_log
        self.selected_folder = ctk.StringVar(value="No folder selected")
        self.report: AssistantReport | None = None
        self.queue: queue.Queue = queue.Queue()

        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(5, weight=1)

        ctk.CTkLabel(self, text="AI Assistant", font=ctk.CTkFont(size=32, weight="bold"), text_color=COLORS["text"]).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 6)
        )
        ctk.CTkLabel(
            self,
            text="Local cleanup intelligence for scan summaries, safe recommendations, and suggested folder structure.",
            font=ctk.CTkFont(size=15),
            text_color=COLORS["muted"],
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 18))

        folder_box = ctk.CTkFrame(self, corner_radius=18, fg_color=COLORS["surface"])
        folder_box.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 14))
        folder_box.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(folder_box, textvariable=self.selected_folder, anchor="w", text_color=COLORS["text"]).grid(
            row=0, column=0, padx=18, pady=14, sticky="ew"
        )
        ctk.CTkButton(folder_box, text="Browse", width=120, height=40, command=self.select_folder).grid(
            row=0, column=1, padx=18, pady=14
        )

        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 14))
        self.analyze_button = ctk.CTkButton(actions, text="Analyze Folder", height=42, corner_radius=12, command=self.start_analysis)
        self.analyze_button.grid(row=0, column=0, padx=(0, 12))
        ctk.CTkButton(
            actions,
            text="Export AI Report",
            height=42,
            corner_radius=12,
            fg_color=COLORS["surface_light"],
            hover_color=COLORS["surface_lighter"],
            command=self.export_report,
        ).grid(row=0, column=1, padx=12)

        progress_box = ctk.CTkFrame(self, corner_radius=18, fg_color=COLORS["surface"])
        progress_box.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(0, 14))
        progress_box.grid_columnconfigure(0, weight=1)
        self.progress_label = ctk.CTkLabel(progress_box, text="Progress: 0%", text_color=COLORS["muted"], anchor="w")
        self.progress_label.grid(row=0, column=0, padx=18, pady=(14, 4), sticky="ew")
        self.progress = ctk.CTkProgressBar(progress_box, height=14, corner_radius=8)
        self.progress.grid(row=1, column=0, padx=18, pady=(0, 16), sticky="ew")
        self.progress.set(0)

        output_box = ctk.CTkFrame(self, corner_radius=18, fg_color=COLORS["surface"])
        output_box.grid(row=5, column=0, columnspan=2, sticky="nsew")
        output_box.grid_columnconfigure((0, 1), weight=1)
        output_box.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(output_box, text="Assistant Report", font=ctk.CTkFont(size=17, weight="bold"), text_color=COLORS["text"]).grid(
            row=0, column=0, padx=18, pady=(16, 6), sticky="w"
        )
        ctk.CTkLabel(output_box, text="Suggested Structure", font=ctk.CTkFont(size=17, weight="bold"), text_color=COLORS["text"]).grid(
            row=0, column=1, padx=18, pady=(16, 6), sticky="w"
        )

        self.report_text = ctk.CTkTextbox(output_box, fg_color=COLORS["surface_light"], text_color=COLORS["text"], corner_radius=14)
        self.report_text.grid(row=1, column=0, padx=18, pady=(0, 18), sticky="nsew")
        self.structure_text = ctk.CTkTextbox(output_box, fg_color=COLORS["surface_light"], text_color=COLORS["text"], corner_radius=14)
        self.structure_text.grid(row=1, column=1, padx=18, pady=(0, 18), sticky="nsew")
        self._set_text(self.report_text, "Choose a folder, then run Analyze Folder.\n\nThis v0.6 assistant is local and rule-based. It does not send files to the internet.")
        self._set_text(self.structure_text, "Suggested folder structure will appear here.")

    def _set_text(self, widget: ctk.CTkTextbox, text: str) -> None:
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", text)
        widget.configure(state="disabled")

    def select_folder(self) -> None:
        folder = filedialog.askdirectory()
        if folder:
            self.selected_folder.set(folder)
            self.set_status("AI Assistant folder selected")
            self.add_log(f"AI Assistant folder selected: {folder}")

    def start_analysis(self) -> None:
        folder = self.selected_folder.get()
        if folder == "No folder selected" or not Path(folder).exists():
            self.set_status("Choose a folder first")
            self.add_log("AI analysis cancelled: no valid folder selected.")
            return

        self.analyze_button.configure(state="disabled", text="Analyzing...")
        self.progress.set(0)
        self.progress_label.configure(text="Progress: 0%")
        self.set_status("AI Assistant analyzing folder")
        self.add_log("Started AI Assistant analysis...")
        thread = threading.Thread(target=self._worker, args=(folder,), daemon=True)
        thread.start()
        self.after(100, self._process_queue)

    def _worker(self, folder: str) -> None:
        def progress(percent: int, message: str) -> None:
            self.queue.put(("progress", percent, message))

        try:
            report = build_assistant_report(folder, progress)
            self.queue.put(("done", report))
        except Exception as exc:
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
                    _, report = message
                    self._show_report(report)
                    self.analyze_button.configure(state="normal", text="Analyze Folder")
                    return
                elif message[0] == "error":
                    _, error = message
                    self.set_status("AI analysis failed")
                    self.add_log(f"AI Assistant error: {error}")
                    self.analyze_button.configure(state="normal", text="Analyze Folder")
                    return
        except queue.Empty:
            pass
        self.after(100, self._process_queue)

    def _show_report(self, report: AssistantReport) -> None:
        self.report = report
        self.progress.set(1)
        self.progress_label.configure(text="Progress: 100%")
        self.set_status("AI Assistant analysis complete")
        self.add_log(f"AI Assistant analyzed {report.scan.total_files} files totaling {format_size(report.scan.total_size)}.")

        lines = [report.summary, "", "Insights:"]
        for insight in report.insights:
            lines.append(f"• {insight.title}: {insight.detail}")
        lines.append("\nSuggested actions:")
        for action in report.suggested_actions:
            lines.append(f"• {action}")
        self._set_text(self.report_text, "\n".join(lines))

        structure_lines: list[str] = []
        for parent, children in report.suggested_structure.items():
            structure_lines.append(f"{parent}/")
            for child in children:
                structure_lines.append(f"  └─ {child}/")
            structure_lines.append("")
        self._set_text(self.structure_text, "\n".join(structure_lines).strip())

    def export_report(self) -> None:
        if self.report is None:
            self.set_status("No AI report to export")
            self.add_log("AI report export cancelled: run analysis first.")
            return
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        report_path = logs_dir / f"ai_assistant_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        report_path.write_text(export_assistant_report(self.report), encoding="utf-8")
        self.set_status("AI report exported")
        self.add_log(f"AI report exported: {report_path}")
