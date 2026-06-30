from __future__ import annotations

import queue
import threading
from datetime import datetime
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk

from src.core.scanner import CATEGORY_EXTENSIONS, format_size
from src.core.search import FileSearchResult, build_search_report, preview_file, search_files
from src.ui.theme import COLORS


class SearchPage(ctk.CTkFrame):
    def __init__(self, parent, set_status, add_log):
        super().__init__(parent, corner_radius=22, fg_color=COLORS["background"])
        self.set_status = set_status
        self.add_log = add_log
        self.selected_folder = ctk.StringVar(value="No folder selected")
        self.query_text = ctk.StringVar(value="")
        self.category = ctk.StringVar(value="All")
        self.result: FileSearchResult | None = None
        self.queue: queue.Queue = queue.Queue()

        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(5, weight=1)

        ctk.CTkLabel(self, text="Scanner Search", font=ctk.CTkFont(size=32, weight="bold"), text_color=COLORS["text"]).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 6)
        )
        ctk.CTkLabel(
            self,
            text="Search by filename, filter by category, preview safe text files, and export search reports.",
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

        controls = ctk.CTkFrame(self, corner_radius=18, fg_color=COLORS["surface"])
        controls.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 14))
        controls.grid_columnconfigure(0, weight=1)
        self.search_entry = ctk.CTkEntry(controls, textvariable=self.query_text, placeholder_text="Search filenames, example: invoice, jpg, project")
        self.search_entry.grid(row=0, column=0, padx=18, pady=16, sticky="ew")
        categories = ["All"] + sorted(CATEGORY_EXTENSIONS.keys()) + ["Other"]
        ctk.CTkOptionMenu(controls, values=categories, variable=self.category, width=160).grid(row=0, column=1, padx=(0, 12), pady=16)
        self.search_button = ctk.CTkButton(controls, text="Search", height=40, command=self.start_search)
        self.search_button.grid(row=0, column=2, padx=(0, 12), pady=16)
        ctk.CTkButton(controls, text="Export", height=40, fg_color=COLORS["surface_light"], hover_color=COLORS["surface_lighter"], command=self.export_report).grid(
            row=0, column=3, padx=(0, 18), pady=16
        )

        progress_box = ctk.CTkFrame(self, corner_radius=18, fg_color=COLORS["surface"])
        progress_box.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(0, 14))
        progress_box.grid_columnconfigure(0, weight=1)
        self.progress_label = ctk.CTkLabel(progress_box, text="Progress: 0%", text_color=COLORS["muted"], anchor="w")
        self.progress_label.grid(row=0, column=0, padx=18, pady=(14, 4), sticky="ew")
        self.progress = ctk.CTkProgressBar(progress_box, height=14, corner_radius=8)
        self.progress.grid(row=1, column=0, padx=18, pady=(0, 16), sticky="ew")
        self.progress.set(0)

        results_box = ctk.CTkFrame(self, corner_radius=18, fg_color=COLORS["surface"])
        results_box.grid(row=5, column=0, columnspan=2, sticky="nsew")
        results_box.grid_columnconfigure((0, 1), weight=1)
        results_box.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(results_box, text="Results", font=ctk.CTkFont(size=17, weight="bold"), text_color=COLORS["text"]).grid(
            row=0, column=0, padx=18, pady=(16, 6), sticky="w"
        )
        ctk.CTkLabel(results_box, text="Preview", font=ctk.CTkFont(size=17, weight="bold"), text_color=COLORS["text"]).grid(
            row=0, column=1, padx=18, pady=(16, 6), sticky="w"
        )
        self.results = ctk.CTkTextbox(results_box, fg_color=COLORS["surface_light"], text_color=COLORS["text"], corner_radius=14)
        self.results.grid(row=1, column=0, padx=18, pady=(0, 18), sticky="nsew")
        self.preview = ctk.CTkTextbox(results_box, fg_color=COLORS["surface_light"], text_color=COLORS["text"], corner_radius=14)
        self.preview.grid(row=1, column=1, padx=18, pady=(0, 18), sticky="nsew")
        self._set_text(self.results, "Choose a folder and run a search.")
        self._set_text(self.preview, "Click Preview First Match after a search, or export the result list.")
        ctk.CTkButton(results_box, text="Preview First Match", height=36, command=self.preview_first_match).grid(
            row=2, column=1, padx=18, pady=(0, 18), sticky="e"
        )

    def _set_text(self, widget: ctk.CTkTextbox, text: str) -> None:
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", text)
        widget.configure(state="disabled")

    def select_folder(self) -> None:
        folder = filedialog.askdirectory()
        if folder:
            self.selected_folder.set(folder)
            self.set_status("Search folder selected")
            self.add_log(f"Search folder selected: {folder}")

    def start_search(self) -> None:
        folder = self.selected_folder.get()
        if folder == "No folder selected" or not Path(folder).exists():
            self.set_status("Choose a folder first")
            self.add_log("Search cancelled: no valid folder selected.")
            return
        self.search_button.configure(state="disabled", text="Searching...")
        self.progress.set(0)
        self.progress_label.configure(text="Progress: 0%")
        self.set_status("Searching files")
        self.add_log("Started file search...")
        thread = threading.Thread(target=self._worker, args=(folder, self.query_text.get(), self.category.get()), daemon=True)
        thread.start()
        self.after(100, self._process_queue)

    def _worker(self, folder: str, query: str, category: str) -> None:
        def progress(percent: int, message: str) -> None:
            self.queue.put(("progress", percent, message))
        try:
            result = search_files(folder, query, category, progress)
            self.queue.put(("done", result))
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
                    _, result = message
                    self._show_result(result)
                    self.search_button.configure(state="normal", text="Search")
                    return
                elif message[0] == "error":
                    _, error = message
                    self.set_status("Search failed")
                    self.add_log(f"Search error: {error}")
                    self.search_button.configure(state="normal", text="Search")
                    return
        except queue.Empty:
            pass
        self.after(100, self._process_queue)

    def _show_result(self, result: FileSearchResult) -> None:
        self.result = result
        self.progress.set(1)
        self.progress_label.configure(text="Progress: 100%")
        self.set_status("Search complete")
        self.add_log(f"Search complete: {len(result.matches)} matches from {result.scanned_files} files.")
        if not result.matches:
            self._set_text(self.results, "No matching files found.")
            self._set_text(self.preview, "No file available to preview.")
            return
        lines = [f"Matches: {len(result.matches)}", ""]
        for item in result.matches[:80]:
            lines.append(f"[{item.category}] {item.name} — {format_size(item.size)}")
            lines.append(f"  {item.path}")
        if len(result.matches) > 80:
            lines.append(f"\n...and {len(result.matches) - 80} more matches. Export the report for the full list.")
        self._set_text(self.results, "\n".join(lines))
        self._set_text(self.preview, "Search complete. Use Preview First Match to inspect the first result.")

    def preview_first_match(self) -> None:
        if self.result is None or not self.result.matches:
            self.set_status("No search result to preview")
            return
        self._set_text(self.preview, preview_file(self.result.matches[0].path))
        self.set_status("Preview loaded")
        self.add_log(f"Previewed: {self.result.matches[0].name}")

    def export_report(self) -> None:
        if self.result is None:
            self.set_status("No search report to export")
            self.add_log("Search export cancelled: run a search first.")
            return
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        report_path = logs_dir / f"search_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        report_path.write_text(build_search_report(self.result), encoding="utf-8")
        self.set_status("Search report exported")
        self.add_log(f"Search report exported: {report_path}")
