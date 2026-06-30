from __future__ import annotations

import queue
import threading
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from src.core.organizer import OrganizationPlan, build_organization_plan, execute_plan, undo_last_organization
from src.core.scanner import format_size
from src.core.settings import load_settings
from src.ui.theme import COLORS


class OrganizerPage(ctk.CTkFrame):
    def __init__(self, parent, set_status, add_log):
        super().__init__(parent, corner_radius=22, fg_color=COLORS["background"])
        self.set_status = set_status
        self.add_log = add_log
        self.selected_folder = ctk.StringVar(value="No folder selected")
        self.plan: OrganizationPlan | None = None
        self.queue: queue.Queue = queue.Queue()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)

        ctk.CTkLabel(self, text="Organizer", font=ctk.CTkFont(size=32, weight="bold"), text_color=COLORS["text"]).grid(row=0, column=0, sticky="w", pady=(0, 6))
        ctk.CTkLabel(self, text="Preview, organize, and undo file moves from one focused workspace.", font=ctk.CTkFont(size=15), text_color=COLORS["muted"]).grid(row=1, column=0, sticky="w", pady=(0, 18))

        folder_box = ctk.CTkFrame(self, corner_radius=18, fg_color=COLORS["surface"])
        folder_box.grid(row=2, column=0, sticky="ew", pady=(0, 14))
        folder_box.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(folder_box, textvariable=self.selected_folder, anchor="w", text_color=COLORS["text"]).grid(row=0, column=0, padx=18, pady=14, sticky="ew")
        ctk.CTkButton(folder_box, text="Browse", width=120, height=40, command=self.select_folder).grid(row=0, column=1, padx=18, pady=14)

        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.grid(row=3, column=0, sticky="ew", pady=(0, 14))
        self.preview_button = ctk.CTkButton(actions, text="Preview Organization", height=42, corner_radius=12, command=self.preview_plan)
        self.preview_button.grid(row=0, column=0, padx=(0, 12))
        self.organize_button = ctk.CTkButton(actions, text="Organize Files", height=42, corner_radius=12, fg_color=COLORS["success"], command=self.start_organize)
        self.organize_button.grid(row=0, column=1, padx=12)
        self.undo_button = ctk.CTkButton(actions, text="Undo Last Organization", height=42, corner_radius=12, fg_color=COLORS["warning"], command=self.start_undo)
        self.undo_button.grid(row=0, column=2, padx=12)
        ctk.CTkButton(actions, text="Clear Preview", height=42, corner_radius=12, fg_color=COLORS["surface_light"], hover_color=COLORS["surface_lighter"], command=self.clear_preview).grid(row=0, column=3, padx=12)

        stats = ctk.CTkFrame(self, corner_radius=18, fg_color=COLORS["surface"])
        stats.grid(row=4, column=0, sticky="ew", pady=(0, 14))
        stats.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.move_count = self._stat(stats, 0, "Planned Moves", "0")
        self.skip_count = self._stat(stats, 1, "Skipped", "0")
        self.category_count = self._stat(stats, 2, "Categories", "0")
        self.total_size = self._stat(stats, 3, "Moving Size", "0 B")

        output = ctk.CTkFrame(self, corner_radius=18, fg_color=COLORS["surface"])
        output.grid(row=5, column=0, sticky="nsew")
        output.grid_columnconfigure((0, 1), weight=1)
        output.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(output, text="Move Preview", font=ctk.CTkFont(size=17, weight="bold"), text_color=COLORS["text"]).grid(row=0, column=0, padx=18, pady=(16, 6), sticky="w")
        ctk.CTkLabel(output, text="Category Summary", font=ctk.CTkFont(size=17, weight="bold"), text_color=COLORS["text"]).grid(row=0, column=1, padx=18, pady=(16, 6), sticky="w")
        self.preview_text = ctk.CTkTextbox(output, fg_color=COLORS["surface_light"], text_color=COLORS["text"], corner_radius=14)
        self.preview_text.grid(row=1, column=0, padx=18, pady=(0, 18), sticky="nsew")
        self.summary_text = ctk.CTkTextbox(output, fg_color=COLORS["surface_light"], text_color=COLORS["text"], corner_radius=14)
        self.summary_text.grid(row=1, column=1, padx=18, pady=(0, 18), sticky="nsew")
        self._set_text(self.preview_text, "Choose a folder and click Preview Organization.")
        self._set_text(self.summary_text, "Category totals will appear here.")

    def _stat(self, parent, column: int, title: str, value: str):
        frame = ctk.CTkFrame(parent, corner_radius=14, fg_color=COLORS["surface_light"])
        frame.grid(row=0, column=column, padx=10, pady=14, sticky="ew")
        ctk.CTkLabel(frame, text=title, text_color=COLORS["muted"]).pack(anchor="w", padx=14, pady=(12, 2))
        label = ctk.CTkLabel(frame, text=value, font=ctk.CTkFont(size=22, weight="bold"), text_color=COLORS["text"])
        label.pack(anchor="w", padx=14, pady=(0, 12))
        return label

    def _set_text(self, widget: ctk.CTkTextbox, text: str) -> None:
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", text)
        widget.configure(state="disabled")

    def select_folder(self) -> None:
        folder = filedialog.askdirectory()
        if folder:
            self.selected_folder.set(folder)
            self.plan = None
            self.set_status("Organizer folder selected")
            self.add_log(f"Organizer folder selected: {folder}")

    def _valid_folder(self) -> str | None:
        folder = self.selected_folder.get()
        if folder == "No folder selected" or not Path(folder).exists():
            self.set_status("Choose a folder first")
            self.add_log("Organizer action cancelled: no valid folder selected.")
            return None
        return folder

    def preview_plan(self) -> None:
        folder = self._valid_folder()
        if not folder:
            return
        self.set_status("Building organization preview")
        self.add_log("Building organizer preview...")
        self.plan = build_organization_plan(folder)
        self._show_plan(self.plan)
        self.set_status("Organization preview ready")
        self.add_log(f"Organizer preview ready: {self.plan.total_files} planned moves.")

    def _show_plan(self, plan: OrganizationPlan) -> None:
        total_bytes = sum(move.size for move in plan.moves)
        self.move_count.configure(text=str(plan.total_files))
        self.skip_count.configure(text=str(len(plan.skipped)))
        self.category_count.configure(text=str(len(plan.categories)))
        self.total_size.configure(text=format_size(total_bytes))

        lines = []
        for move in plan.moves[:120]:
            lines.append(f"{Path(move.source).name}  →  {move.category}/{Path(move.destination).name}")
        if plan.total_files > 120:
            lines.append(f"\n...and {plan.total_files - 120} more planned moves.")
        if not lines:
            lines.append("No moves needed. This folder may already be organized or empty.")
        self._set_text(self.preview_text, "\n".join(lines))

        summary = [f"{category}: {count}" for category, count in sorted(plan.categories.items())]
        if plan.skipped:
            summary.append(f"\nSkipped protected/already organized files: {len(plan.skipped)}")
        self._set_text(self.summary_text, "\n".join(summary) if summary else "No categories found.")

    def clear_preview(self) -> None:
        self.plan = None
        self.move_count.configure(text="0")
        self.skip_count.configure(text="0")
        self.category_count.configure(text="0")
        self.total_size.configure(text="0 B")
        self._set_text(self.preview_text, "Preview cleared.")
        self._set_text(self.summary_text, "Category totals will appear here.")
        self.set_status("Organizer preview cleared")

    def start_organize(self) -> None:
        folder = self._valid_folder()
        if not folder:
            return
        settings = load_settings()
        if self.plan is None:
            if settings.preview_before_organize:
                self.plan = build_organization_plan(folder)
                self._show_plan(self.plan)
                self.set_status("Preview created first. Review it, then click Organize Files again.")
                self.add_log("Safety setting required preview before organizing.")
                return
            self.plan = build_organization_plan(folder)
            self._show_plan(self.plan)
        if self.plan.total_files == 0:
            self.set_status("No files to organize")
            return
        if settings.confirm_before_organize:
            if not messagebox.askyesno("Confirm Organization", f"Move {self.plan.total_files} files into category folders?\n\nAn undo manifest will be saved."):
                self.set_status("Organization cancelled")
                return
        self._set_buttons("disabled")
        thread = threading.Thread(target=self._organize_worker, daemon=True)
        thread.start()
        self.after(100, self._process_queue)

    def _organize_worker(self) -> None:
        def progress(percent: int, message: str) -> None:
            self.queue.put(("progress", percent, message))
        result = execute_plan(self.plan, progress)  # type: ignore[arg-type]
        self.queue.put(("organized", result))

    def start_undo(self) -> None:
        if not messagebox.askyesno("Undo Last Organization", "Move files from the latest manifest back to their original locations?"):
            return
        self._set_buttons("disabled")
        thread = threading.Thread(target=self._undo_worker, daemon=True)
        thread.start()
        self.after(100, self._process_queue)

    def _undo_worker(self) -> None:
        def progress(percent: int, message: str) -> None:
            self.queue.put(("progress", percent, message))
        result = undo_last_organization(progress_callback=progress)
        self.queue.put(("undone", result))

    def _process_queue(self) -> None:
        try:
            while True:
                message = self.queue.get_nowait()
                if message[0] == "progress":
                    _, _percent, text = message
                    self.set_status(text)
                elif message[0] in {"organized", "undone"}:
                    action, result = message
                    self._set_buttons("normal")
                    self.set_status(f"{action.title()} complete")
                    self.add_log(f"Organizer {action}: moved {result.moved_files}, skipped {result.skipped_files}, errors {len(result.errors)}.")
                    self.preview_plan() if action == "undone" and self._valid_folder() else None
                    return
        except queue.Empty:
            pass
        self.after(100, self._process_queue)

    def _set_buttons(self, state: str) -> None:
        self.preview_button.configure(state=state)
        self.organize_button.configure(state=state)
        self.undo_button.configure(state=state)
