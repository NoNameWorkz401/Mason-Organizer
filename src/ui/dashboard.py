from __future__ import annotations

import queue
import threading
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from src.core.organizer import OrganizationPlan, build_organization_plan, execute_plan, undo_last_organization
from src.core.scanner import ScanResult, format_size, scan_folder
from src.ui.theme import CATEGORY_COLORS, COLORS


def _category_color(name: str) -> str:
    return CATEGORY_COLORS.get(name, CATEGORY_COLORS.get(name.title(), CATEGORY_COLORS["Other"]))


class GlassCard(ctk.CTkFrame):
    """Reusable card styled to match the v0.9 visual direction."""

    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            corner_radius=14,
            fg_color=COLORS["surface"],
            border_width=1,
            border_color=COLORS["card_border"],
            **kwargs,
        )


class StatCard(GlassCard):
    def __init__(self, parent, title: str, value: str, subtitle: str, icon: str, icon_color: str):
        super().__init__(parent)
        self.grid_columnconfigure(1, weight=1)

        icon_box = ctk.CTkFrame(self, width=58, height=58, corner_radius=12, fg_color=icon_color)
        icon_box.grid(row=0, column=0, rowspan=3, padx=(18, 14), pady=20, sticky="w")
        icon_box.grid_propagate(False)
        ctk.CTkLabel(icon_box, text=icon, font=ctk.CTkFont(size=28), text_color=COLORS["text"]).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(self, text=title, font=ctk.CTkFont(size=14), text_color=COLORS["text"], anchor="w").grid(
            row=0, column=1, padx=(0, 12), pady=(20, 0), sticky="ew"
        )
        self.value_label = ctk.CTkLabel(
            self, text=value, font=ctk.CTkFont(size=26, weight="bold"), text_color=COLORS["text"], anchor="w"
        )
        self.value_label.grid(row=1, column=1, padx=(0, 12), sticky="ew")
        self.subtitle_label = ctk.CTkLabel(self, text=subtitle, font=ctk.CTkFont(size=13), text_color=COLORS["muted"], anchor="w")
        self.subtitle_label.grid(row=2, column=1, padx=(0, 12), pady=(0, 18), sticky="ew")

    def set_value(self, value: str, subtitle: str | None = None) -> None:
        self.value_label.configure(text=value)
        if subtitle is not None:
            self.subtitle_label.configure(text=subtitle)


class Dashboard(ctk.CTkFrame):
    def __init__(self, parent, set_status, add_log, navigate=None):
        super().__init__(parent, corner_radius=0, fg_color=COLORS["background"])
        self.set_status = set_status
        self.add_log = add_log
        self.navigate = navigate
        self.selected_folder = ctk.StringVar(value="No folder selected")
        self.result: ScanResult | None = None
        self.organization_plan: OrganizationPlan | None = None
        self.scan_queue: queue.Queue = queue.Queue()
        self.organize_queue: queue.Queue = queue.Queue()
        self.activity_rows: list[ctk.CTkFrame] = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.main = ctk.CTkScrollableFrame(self, corner_radius=0, fg_color=COLORS["background"])
        self.main.grid(row=0, column=0, sticky="nsew")
        self.main.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="stats")

        self._build_header()
        self._build_stats()
        self._build_main_panels()
        self._build_activity_log()

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self.main, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=4, sticky="ew", pady=(4, 18))
        header.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure(1, weight=0)

        ctk.CTkLabel(
            header,
            text="Dashboard",
            font=ctk.CTkFont(size=30, weight="bold"),
            text_color=COLORS["text"],
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            header,
            text="Welcome back, Mason! Here's an overview of your files.",
            font=ctk.CTkFont(size=15),
            text_color=COLORS["muted"],
        ).grid(row=1, column=0, sticky="w", pady=(6, 0))

        folder_area = ctk.CTkFrame(header, fg_color="transparent")
        folder_area.grid(row=0, column=1, rowspan=2, sticky="e")
        folder_area.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(folder_area, text="Current Folder", text_color=COLORS["text"], anchor="w").grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=(0, 6)
        )
        folder_entry = ctk.CTkEntry(
            folder_area,
            textvariable=self.selected_folder,
            width=360,
            height=44,
            corner_radius=8,
            fg_color=COLORS["input"],
            border_color=COLORS["border"],
            text_color=COLORS["text"],
        )
        folder_entry.grid(row=1, column=0, padx=(0, 12), sticky="ew")
        ctk.CTkButton(
            folder_area,
            text="□  Change",
            width=128,
            height=44,
            corner_radius=8,
            fg_color=COLORS["primary_dark"],
            hover_color=COLORS["secondary"],
            command=self.select_folder,
        ).grid(row=1, column=1)

    def _build_stats(self) -> None:
        self.files_card = StatCard(self.main, "Total Files", "0", "files", "▧", COLORS["primary_dark"])
        self.files_card.grid(row=1, column=0, padx=(0, 8), pady=(0, 18), sticky="nsew")
        self.folders_card = StatCard(self.main, "Total Folders", "0", "folders", "□", COLORS["success_dark"])
        self.folders_card.grid(row=1, column=1, padx=8, pady=(0, 18), sticky="nsew")
        self.size_card = StatCard(self.main, "Total Size", "0 MB", "0 bytes", "▱", COLORS["secondary"])
        self.size_card.grid(row=1, column=2, padx=8, pady=(0, 18), sticky="nsew")
        self.categories_card = StatCard(self.main, "File Categories", "0", "types", "▧", COLORS["orange"])
        self.categories_card.grid(row=1, column=3, padx=8, pady=(0, 18), sticky="nsew")
        self.last_scan_card = StatCard(self.main, "Last Scan", "Never", "not scanned", "▣", COLORS["accent"])
        self.last_scan_card.grid(row=2, column=0, padx=(0, 8), pady=(0, 18), sticky="nsew")

    def _build_main_panels(self) -> None:
        categories = GlassCard(self.main)
        categories.grid(row=3, column=0, columnspan=2, padx=(0, 8), pady=(0, 18), sticky="nsew")
        categories.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(categories, text="File Categories", font=ctk.CTkFont(size=21, weight="bold"), text_color=COLORS["text"]).grid(
            row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="w"
        )
        self.chart_canvas = tk.Canvas(categories, width=210, height=210, bg=COLORS["surface"], highlightthickness=0)
        self.chart_canvas.grid(row=1, column=0, padx=(20, 10), pady=10)
        self.legend_frame = ctk.CTkFrame(categories, fg_color="transparent")
        self.legend_frame.grid(row=1, column=1, padx=(6, 20), pady=10, sticky="nsew")
        ctk.CTkButton(
            categories,
            text="View Analytics",
            height=38,
            corner_radius=8,
            fg_color=COLORS["surface_light"],
            hover_color=COLORS["primary_dark"],
            command=lambda: self.navigate("analytics") if self.navigate else None,
        ).grid(row=2, column=0, columnspan=2, pady=(4, 20))

        largest = GlassCard(self.main)
        largest.grid(row=3, column=2, padx=8, pady=(0, 18), sticky="nsew")
        largest.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(largest, text="Largest Files", font=ctk.CTkFont(size=21, weight="bold"), text_color=COLORS["text"]).grid(
            row=0, column=0, padx=20, pady=(20, 12), sticky="w"
        )
        self.largest_frame = ctk.CTkFrame(largest, fg_color="transparent")
        self.largest_frame.grid(row=1, column=0, padx=20, sticky="nsew")
        ctk.CTkButton(
            largest,
            text="View All",
            height=38,
            corner_radius=8,
            fg_color=COLORS["surface_light"],
            hover_color=COLORS["primary_dark"],
            command=lambda: self.navigate("search") if self.navigate else None,
        ).grid(row=2, column=0, pady=(14, 20))

        progress = GlassCard(self.main)
        progress.grid(row=3, column=3, columnspan=1, padx=(8, 0), pady=(0, 18), sticky="nsew")
        progress.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(progress, text="Scan Progress", font=ctk.CTkFont(size=21, weight="bold"), text_color=COLORS["text"]).grid(
            row=0, column=0, padx=20, pady=(20, 22), sticky="w"
        )
        progress_status = ctk.CTkFrame(progress, fg_color="transparent")
        progress_status.grid(row=1, column=0, padx=20, sticky="ew")
        progress_status.grid_columnconfigure(0, weight=1)
        self.progress_message = ctk.CTkLabel(progress_status, text="Ready to scan", text_color=COLORS["text"], anchor="w")
        self.progress_message.grid(row=0, column=0, sticky="w")
        self.progress_percent = ctk.CTkLabel(progress_status, text="0%", font=ctk.CTkFont(size=18), text_color=COLORS["text"])
        self.progress_percent.grid(row=0, column=1, sticky="e")
        self.progress = ctk.CTkProgressBar(progress, height=12, corner_radius=6, progress_color=COLORS["secondary"])
        self.progress.grid(row=2, column=0, padx=20, pady=(22, 28), sticky="ew")
        self.progress.set(0)
        self.progress_detail = ctk.CTkLabel(progress, text="No folder scanned yet.\nSelect a folder and run Scan Folder.", text_color=COLORS["muted"], justify="left")
        self.progress_detail.grid(row=3, column=0, padx=20, sticky="w")

        action_row = ctk.CTkFrame(progress, fg_color="transparent")
        action_row.grid(row=4, column=0, pady=(32, 20))
        self.scan_button = ctk.CTkButton(
            action_row,
            text="⟳  Scan Folder",
            width=156,
            height=44,
            corner_radius=8,
            fg_color=COLORS["primary_dark"],
            hover_color=COLORS["secondary"],
            command=self.start_scan,
        )
        self.scan_button.grid(row=0, column=0, padx=6)
        self.preview_button = ctk.CTkButton(action_row, text="Preview", width=100, height=44, corner_radius=8, fg_color=COLORS["surface_light"], command=self.preview_organization)
        self.preview_button.grid(row=0, column=1, padx=6)
        self.organize_button = ctk.CTkButton(action_row, text="Organize", width=108, height=44, corner_radius=8, fg_color=COLORS["success_dark"], command=self.start_organize)
        self.organize_button.grid(row=1, column=0, padx=6, pady=(10,0))
        self.undo_button = ctk.CTkButton(action_row, text="Undo", width=86, height=44, corner_radius=8, fg_color=COLORS["warning"], command=self.start_undo)
        self.undo_button.grid(row=1, column=1, padx=6, pady=(10,0))

        self._draw_empty_chart()
        self._populate_largest([])
        self._populate_legend({})

    def _build_activity_log(self) -> None:
        activity = GlassCard(self.main)
        activity.grid(row=4, column=0, columnspan=4, sticky="nsew")
        activity.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(activity, text="Activity Log", font=ctk.CTkFont(size=20, weight="bold"), text_color=COLORS["text"]).grid(
            row=0, column=0, padx=20, pady=(18, 8), sticky="w"
        )
        ctk.CTkButton(
            activity,
            text="View Full Log  ↗",
            width=130,
            height=34,
            corner_radius=8,
            fg_color="transparent",
            hover_color=COLORS["surface_light"],
            text_color=COLORS["primary"],
            command=lambda: self.navigate("logs") if self.navigate else None,
        ).grid(row=0, column=1, padx=20, pady=(18, 8), sticky="e")
        self.activity_list = ctk.CTkFrame(activity, fg_color=COLORS["input"], corner_radius=10, border_width=1, border_color=COLORS["border"])
        self.activity_list.grid(row=1, column=0, columnspan=2, padx=14, pady=(0, 14), sticky="nsew")
        self.add_activity("Application started")

    def add_activity(self, message: str) -> None:
        if not hasattr(self, "activity_list"):
            return
        timestamp = datetime.now().strftime("%H:%M:%S")
        row = ctk.CTkFrame(self.activity_list, fg_color="transparent")
        row.pack(fill="x", padx=10, pady=1)
        ctk.CTkLabel(row, text="●", text_color=COLORS["success"], width=22).pack(side="left")
        ctk.CTkLabel(row, text=timestamp, text_color=COLORS["muted"], width=78, anchor="w").pack(side="left")
        ctk.CTkLabel(row, text=message, text_color=COLORS["text"], anchor="w").pack(side="left", fill="x", expand=True)
        self.activity_rows.append(row)
        while len(self.activity_rows) > 4:
            old = self.activity_rows.pop(0)
            old.destroy()

    def _draw_empty_chart(self) -> None:
        self.chart_canvas.delete("all")
        self.chart_canvas.create_oval(28, 28, 182, 182, fill=COLORS["surface_light"], outline="")
        self.chart_canvas.create_oval(76, 76, 134, 134, fill=COLORS["surface"], outline="")

    def _draw_donut(self, categories: dict[str, int]) -> None:
        self.chart_canvas.delete("all")
        total = sum(categories.values())
        if total <= 0:
            self._draw_empty_chart()
            return
        start = 90
        for name, count in sorted(categories.items(), key=lambda item: item[1], reverse=True):
            extent = -(count / total) * 360
            self.chart_canvas.create_arc(24, 24, 186, 186, start=start, extent=extent, fill=_category_color(name), outline="")
            start += extent
        self.chart_canvas.create_oval(76, 76, 134, 134, fill=COLORS["surface"], outline="")

    def _populate_legend(self, categories: dict[str, int]) -> None:
        for child in self.legend_frame.winfo_children():
            child.destroy()
        if not categories:
            ctk.CTkLabel(self.legend_frame, text="Scan a folder to see categories.", text_color=COLORS["muted"], justify="left").pack(anchor="w", pady=10)
            return
        total = sum(categories.values()) or 1
        for name, count in sorted(categories.items(), key=lambda item: item[1], reverse=True)[:7]:
            row = ctk.CTkFrame(self.legend_frame, fg_color="transparent")
            row.pack(fill="x", pady=4)
            ctk.CTkLabel(row, text="■", text_color=_category_color(name), width=22).pack(side="left")
            ctk.CTkLabel(row, text=name, text_color=COLORS["text"], anchor="w", width=92).pack(side="left")
            ctk.CTkLabel(row, text=f"{count} ({count / total:.1%})", text_color=COLORS["muted"], anchor="e").pack(side="right")

    def _populate_largest(self, largest_files: list[tuple[str, int]]) -> None:
        for child in self.largest_frame.winfo_children():
            child.destroy()
        if not largest_files:
            ctk.CTkLabel(self.largest_frame, text="Scan a folder to see largest files.", text_color=COLORS["muted"], justify="left").pack(anchor="w", pady=10)
            return
        for path, size in largest_files[:5]:
            row = ctk.CTkFrame(self.largest_frame, fg_color="transparent")
            row.pack(fill="x", pady=8)
            ctk.CTkLabel(row, text="▣", text_color=COLORS["primary"], width=28).pack(side="left")
            ctk.CTkLabel(row, text=Path(path).name, text_color=COLORS["text"], anchor="w").pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(row, text=format_size(size), text_color=COLORS["muted"], anchor="e").pack(side="right")

    def select_folder(self) -> None:
        folder = filedialog.askdirectory()
        if folder:
            self.selected_folder.set(folder)
            self.set_status("Folder selected")
            self.add_log(f"Folder changed to: {folder}")

    def start_scan(self) -> None:
        folder = self.selected_folder.get()
        if folder == "No folder selected" or not Path(folder).exists():
            self.set_status("Choose a folder first")
            self.add_log("Scan cancelled: no valid folder selected.")
            return

        self.scan_button.configure(state="disabled", text="Scanning...")
        self.progress.set(0)
        self.progress_percent.configure(text="0%")
        self.progress_message.configure(text="Scanning folder")
        self.progress_detail.configure(text="Preparing scan...")
        self.set_status("Scanning folder")
        self.add_log(f"Scan started: {folder}")

        thread = threading.Thread(target=self._scan_worker, args=(folder,), daemon=True)
        thread.start()
        self.after(100, self._process_scan_queue)

    def _scan_worker(self, folder: str) -> None:
        def progress(percent: int, message: str) -> None:
            self.scan_queue.put(("progress", percent, message))

        try:
            result = scan_folder(folder, progress)
            self.scan_queue.put(("done", result))
        except Exception as exc:
            self.scan_queue.put(("error", str(exc)))

    def _process_scan_queue(self) -> None:
        try:
            while True:
                message = self.scan_queue.get_nowait()
                if message[0] == "progress":
                    _, percent, text = message
                    self.progress.set(percent / 100)
                    self.progress_percent.configure(text=f"{percent}%")
                    self.progress_message.configure(text=text)
                    self.set_status(text)
                elif message[0] == "done":
                    _, result = message
                    self._show_result(result)
                    self.scan_button.configure(state="normal", text="⟳  Scan Again")
                    return
                elif message[0] == "error":
                    _, error = message
                    self.set_status("Scan failed")
                    self.add_log(f"Scan error: {error}")
                    self.scan_button.configure(state="normal", text="⟳  Scan Folder")
                    return
        except queue.Empty:
            pass
        self.after(100, self._process_scan_queue)

    def _show_result(self, result: ScanResult) -> None:
        self.result = result
        self.files_card.set_value(f"{result.total_files:,}", "files")
        self.folders_card.set_value(f"{result.total_folders:,}", "folders")
        self.size_card.set_value(format_size(result.total_size), f"{result.total_size:,} bytes")
        self.categories_card.set_value(str(len(result.categories)), "types")
        self.last_scan_card.set_value("Today", datetime.now().strftime("%I:%M %p"))
        self.progress.set(1)
        self.progress_percent.configure(text="100%")
        self.progress_message.configure(text="Folder scanning completed")
        self.progress_detail.configure(text=f"{result.total_files:,} files scanned\n{format_size(result.total_size)} found")
        self._draw_donut(result.categories)
        self._populate_legend(result.categories)
        self._populate_largest(result.largest_files)
        self.set_status("Scan complete")
        self.add_log(f"Scan completed: {result.total_files:,} files found ({format_size(result.total_size)})")

    def preview_organization(self) -> None:
        folder = self.selected_folder.get()
        if folder == "No folder selected" or not Path(folder).exists():
            self.set_status("Choose a folder first")
            self.add_log("Preview cancelled: no valid folder selected.")
            return

        self.organization_plan = build_organization_plan(folder)
        plan = self.organization_plan

        if plan.total_files == 0:
            self.set_status("Nothing to organize")
            self.add_log("Organization preview found no files to move.")
            messagebox.showinfo("Preview", "No files need to be moved.")
            return

        summary = [f"{plan.total_files} files ready to organize", ""]
        for category, count in sorted(plan.categories.items()):
            summary.append(f"{category}: {count}")
        self.set_status("Organization preview ready")
        self.add_log(f"Preview ready: {plan.total_files} files can be organized.")
        messagebox.showinfo("Organization Preview", "\n".join(summary[:14]))

    def start_organize(self) -> None:
        folder = self.selected_folder.get()
        if folder == "No folder selected" or not Path(folder).exists():
            self.set_status("Choose a folder first")
            self.add_log("Organization cancelled: no valid folder selected.")
            return

        if self.organization_plan is None:
            self.organization_plan = build_organization_plan(folder)

        if self.organization_plan.total_files == 0:
            self.set_status("Nothing to organize")
            self.add_log("No files need to be organized.")
            return

        confirmed = messagebox.askyesno(
            "Organize files?",
            f"Mason Organizer will move {self.organization_plan.total_files} files into category folders.\n\nAn undo manifest will be created.",
        )
        if not confirmed:
            self.set_status("Organization cancelled")
            self.add_log("Organization cancelled by user.")
            return

        self.organize_button.configure(state="disabled", text="Organizing...")
        self.scan_button.configure(state="disabled")
        self.preview_button.configure(state="disabled")
        self.progress.set(0)
        self.progress_percent.configure(text="0%")
        self.progress_message.configure(text="Organizing files")
        self.progress_detail.configure(text="Moving files safely and creating undo manifest...")
        self.set_status("Organizing files")
        self.add_log("Started file organization...")

        thread = threading.Thread(target=self._organize_worker, daemon=True)
        thread.start()
        self.after(100, self._process_organize_queue)

    def _organize_worker(self) -> None:
        def progress(percent: int, message: str) -> None:
            self.organize_queue.put(("progress", percent, message))

        try:
            result = execute_plan(self.organization_plan, progress)  # type: ignore[arg-type]
            self.organize_queue.put(("done", result))
        except Exception as exc:
            self.organize_queue.put(("error", str(exc)))

    def _process_organize_queue(self) -> None:
        try:
            while True:
                message = self.organize_queue.get_nowait()
                if message[0] == "progress":
                    _, percent, text = message
                    self.progress.set(percent / 100)
                    self.progress_percent.configure(text=f"{percent}%")
                    self.progress_message.configure(text=text)
                    self.set_status(text)
                elif message[0] == "done":
                    _, result = message
                    self.organize_button.configure(state="normal", text="Organize")
                    self.scan_button.configure(state="normal", text="⟳  Scan Again")
                    self.preview_button.configure(state="normal")
                    self.organization_plan = None
                    self.set_status("Organization complete")
                    self.add_log(f"Organization complete: moved {result.moved_files} files, skipped {result.skipped_files}.")
                    if result.manifest_path:
                        self.add_log(f"Undo manifest saved: {result.manifest_path}")
                    if result.errors:
                        self.add_log(f"Organization completed with {len(result.errors)} errors.")
                    self.progress_detail.configure(text="Organization complete. Scan again to refresh totals.")
                    return
                elif message[0] == "error":
                    _, error = message
                    self.set_status("Organization failed")
                    self.add_log(f"Organization error: {error}")
                    self.organize_button.configure(state="normal", text="Organize")
                    self.scan_button.configure(state="normal", text="⟳  Scan Folder")
                    self.preview_button.configure(state="normal")
                    return
        except queue.Empty:
            pass
        self.after(100, self._process_organize_queue)

    def start_undo(self) -> None:
        confirmed = messagebox.askyesno("Undo last organization?", "This will move files from the last organization back to their original locations.")
        if not confirmed:
            return
        try:
            result = undo_last_organization()
            if result.errors:
                self.set_status("Undo had issues")
                self.add_log("Undo issue: " + "; ".join(result.errors[:3]))
            else:
                self.set_status("Undo complete")
                self.add_log(f"Undo complete: moved {result.moved_files} files back, skipped {result.skipped_files}.")
            self.progress_detail.configure(text="Undo complete. Scan the folder again to refresh totals.")
        except Exception as exc:
            self.set_status("Undo failed")
            self.add_log(f"Undo error: {exc}")

    def export_scan_report(self) -> None:
        if self.result is None:
            self.set_status("No scan report to export")
            self.add_log("Scan export cancelled: run a scan first.")
            return

        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        report_path = logs_dir / f"scan_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        lines = [
            "Mason Organizer Scan Report",
            f"Folder: {self.result.folder}",
            f"Files: {self.result.total_files}",
            f"Folders: {self.result.total_folders}",
            f"Total size: {format_size(self.result.total_size)}",
            "",
            "Categories:",
        ]
        if self.result.categories:
            for name, count in sorted(self.result.categories.items()):
                lines.append(f"  - {name}: {count}")
        else:
            lines.append("  - No files found")

        lines.extend(["", "Largest files:"])
        if self.result.largest_files:
            for path, size in self.result.largest_files:
                lines.append(f"  - {Path(path).name}: {format_size(size)} — {path}")
        else:
            lines.append("  - No files found")

        report_path.write_text("\n".join(lines), encoding="utf-8")
        self.set_status("Scan report exported")
        self.add_log(f"Scan report exported: {report_path}")

    def clear_results(self) -> None:
        self.result = None
        self.files_card.set_value("0", "files")
        self.folders_card.set_value("0", "folders")
        self.size_card.set_value("0 MB", "0 bytes")
        self.categories_card.set_value("0", "types")
        self.last_scan_card.set_value("Never", "not scanned")
        self.progress.set(0)
        self.progress_percent.configure(text="0%")
        self.progress_message.configure(text="Ready to scan")
        self.progress_detail.configure(text="No folder scanned yet.\nSelect a folder and run Scan Folder.")
        self._draw_empty_chart()
        self._populate_legend({})
        self._populate_largest([])
        self.organization_plan = None
        self.set_status("Results cleared")
        self.add_log("Dashboard results cleared.")
