from __future__ import annotations

from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from src.core.settings import AppSettings, load_settings, save_settings
from src.ui.theme import COLORS, THEMES


class SettingsPage(ctk.CTkFrame):
    def __init__(self, parent, set_status, add_log, on_theme_change=None):
        super().__init__(parent, corner_radius=22, fg_color=COLORS["background"])
        self.set_status = set_status
        self.add_log = add_log
        self.on_theme_change = on_theme_change
        self.settings: AppSettings = load_settings()

        self.default_folder = ctk.StringVar(value=self.settings.default_folder or "No default folder selected")
        self.preview_var = ctk.BooleanVar(value=self.settings.preview_before_organize)
        self.confirm_var = ctk.BooleanVar(value=self.settings.confirm_before_organize)
        self.hidden_var = ctk.BooleanVar(value=self.settings.include_hidden_files)
        self.accent_var = ctk.StringVar(value=self.settings.accent_theme)
        self.ai_mode_var = ctk.StringVar(value=self.settings.local_ai_mode)
        self.logs_folder = ctk.StringVar(value=self.settings.export_logs_folder)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(self, text="Settings", font=ctk.CTkFont(size=32, weight="bold"), text_color=COLORS["text"]).grid(
            row=0, column=0, sticky="w", pady=(0, 6)
        )
        ctk.CTkLabel(
            self,
            text="Configure safety, folders, theme direction, and local assistant behavior.",
            font=ctk.CTkFont(size=15),
            text_color=COLORS["muted"],
        ).grid(row=1, column=0, sticky="w", pady=(0, 18))

        body = ctk.CTkScrollableFrame(self, corner_radius=18, fg_color=COLORS["surface"])
        body.grid(row=2, column=0, sticky="nsew")
        body.grid_columnconfigure(0, weight=1)

        self._folder_section(body, 0)
        self._safety_section(body, 1)
        self._theme_section(body, 2)
        self._ai_section(body, 3)
        self._actions(body, 4)

    def _section(self, parent, row: int, title: str, subtitle: str) -> ctk.CTkFrame:
        card = ctk.CTkFrame(parent, corner_radius=16, fg_color=COLORS["surface_light"])
        card.grid(row=row, column=0, padx=18, pady=12, sticky="ew")
        card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=18, weight="bold"), text_color=COLORS["text"]).grid(
            row=0, column=0, padx=18, pady=(16, 2), sticky="w"
        )
        ctk.CTkLabel(card, text=subtitle, text_color=COLORS["muted"], anchor="w").grid(
            row=1, column=0, padx=18, pady=(0, 12), sticky="ew"
        )
        return card

    def _folder_section(self, parent, row: int) -> None:
        card = self._section(parent, row, "Default Workspace", "Choose the folder Mason Organizer should remember for future sessions.")
        box = ctk.CTkFrame(card, fg_color=COLORS["input"], corner_radius=12)
        box.grid(row=2, column=0, padx=18, pady=(0, 16), sticky="ew")
        box.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(box, textvariable=self.default_folder, text_color=COLORS["text"], anchor="w").grid(
            row=0, column=0, padx=14, pady=12, sticky="ew"
        )
        ctk.CTkButton(box, text="Browse", width=120, command=self.choose_default_folder).grid(row=0, column=1, padx=12, pady=12)

        logs = ctk.CTkFrame(card, fg_color="transparent")
        logs.grid(row=3, column=0, padx=18, pady=(0, 16), sticky="ew")
        logs.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(logs, text="Reports folder", text_color=COLORS["muted"]).grid(row=0, column=0, padx=(0, 12), sticky="w")
        ctk.CTkEntry(logs, textvariable=self.logs_folder, fg_color=COLORS["input"], border_color=COLORS["border"]).grid(
            row=0, column=1, sticky="ew"
        )

    def _safety_section(self, parent, row: int) -> None:
        card = self._section(parent, row, "Safety Controls", "Keep file moves predictable and reversible.")
        ctk.CTkSwitch(card, text="Require preview before organizing", variable=self.preview_var).grid(
            row=2, column=0, padx=18, pady=8, sticky="w"
        )
        ctk.CTkSwitch(card, text="Confirm before moving files", variable=self.confirm_var).grid(
            row=3, column=0, padx=18, pady=8, sticky="w"
        )
        ctk.CTkSwitch(card, text="Include hidden files in future scans", variable=self.hidden_var).grid(
            row=4, column=0, padx=18, pady=(8, 16), sticky="w"
        )

    def _theme_section(self, parent, row: int) -> None:
        card = self._section(parent, row, "Theme Studio", "Pick a built-in color theme. The interface refreshes immediately after saving.")
        card.grid_columnconfigure(0, weight=1)

        grid = ctk.CTkFrame(card, fg_color="transparent")
        grid.grid(row=2, column=0, padx=18, pady=(0, 12), sticky="ew")
        for col in range(3):
            grid.grid_columnconfigure(col, weight=1)

        for index, (theme_name, palette) in enumerate(THEMES.items()):
            row_index = index // 3
            col_index = index % 3
            theme_card = ctk.CTkButton(
                grid,
                text=f"{theme_name}   ●",
                height=44,
                corner_radius=12,
                fg_color=palette["surface_light"],
                hover_color=palette["primary_dark"],
                text_color=palette["text"],
                command=lambda name=theme_name: self.accent_var.set(name),
            )
            theme_card.grid(row=row_index, column=col_index, padx=6, pady=6, sticky="ew")

        ctk.CTkLabel(card, text="Selected theme", text_color=COLORS["muted"]).grid(
            row=3, column=0, padx=18, pady=(4, 4), sticky="w"
        )
        ctk.CTkOptionMenu(card, variable=self.accent_var, values=list(THEMES.keys())).grid(
            row=4, column=0, padx=18, pady=(0, 16), sticky="w"
        )
        ctk.CTkLabel(
            card,
            text="Use the color cards or dropdown, then click Save Settings. Mason Organizer will repaint the interface instantly.",
            text_color=COLORS["muted"],
            anchor="w",
            wraplength=760,
        ).grid(row=5, column=0, padx=18, pady=(0, 16), sticky="ew")

    def _ai_section(self, parent, row: int) -> None:
        card = self._section(parent, row, "AI Assistant", "Keep assistance local and privacy-first.")
        ctk.CTkOptionMenu(card, variable=self.ai_mode_var, values=["Rule-Based Local", "Future Ollama Local Model"]).grid(
            row=2, column=0, padx=18, pady=(0, 16), sticky="w"
        )
        ctk.CTkLabel(
            card,
            text="Current AI Chat explains sections, workflows, safety, duplicates, and cleanup suggestions without uploading files.",
            text_color=COLORS["muted"],
            anchor="w",
            wraplength=760,
        ).grid(row=3, column=0, padx=18, pady=(0, 16), sticky="ew")

    def _actions(self, parent, row: int) -> None:
        actions = ctk.CTkFrame(parent, fg_color="transparent")
        actions.grid(row=row, column=0, padx=18, pady=(12, 22), sticky="ew")
        ctk.CTkButton(actions, text="Save Settings", height=42, corner_radius=12, command=self.save).grid(
            row=0, column=0, padx=(0, 12)
        )
        ctk.CTkButton(
            actions,
            text="Reset Defaults",
            height=42,
            corner_radius=12,
            fg_color=COLORS["surface_lighter"],
            hover_color=COLORS["secondary"],
            command=self.reset,
        ).grid(row=0, column=1, padx=12)
        ctk.CTkButton(
            actions,
            text="Open Config Folder",
            height=42,
            corner_radius=12,
            fg_color=COLORS["surface_lighter"],
            command=self.open_config_note,
        ).grid(row=0, column=2, padx=12)

    def choose_default_folder(self) -> None:
        folder = filedialog.askdirectory()
        if folder:
            self.default_folder.set(folder)
            self.set_status("Default folder selected")

    def _collect(self) -> AppSettings:
        default_folder = self.default_folder.get()
        if default_folder == "No default folder selected":
            default_folder = ""
        return AppSettings(
            default_folder=default_folder,
            preview_before_organize=self.preview_var.get(),
            confirm_before_organize=self.confirm_var.get(),
            include_hidden_files=self.hidden_var.get(),
            accent_theme=self.accent_var.get(),
            local_ai_mode=self.ai_mode_var.get(),
            export_logs_folder=self.logs_folder.get().strip() or "logs",
        )

    def save(self) -> None:
        self.settings = self._collect()
        path = save_settings(self.settings)
        self.set_status("Settings saved")
        self.add_log(f"Settings saved to {path}")
        if self.on_theme_change:
            self.on_theme_change(self.settings.accent_theme)
        else:
            messagebox.showinfo("Settings Saved", "Mason Organizer settings were saved successfully.")

    def reset(self) -> None:
        self.settings = AppSettings()
        self.default_folder.set("No default folder selected")
        self.preview_var.set(self.settings.preview_before_organize)
        self.confirm_var.set(self.settings.confirm_before_organize)
        self.hidden_var.set(self.settings.include_hidden_files)
        self.accent_var.set(self.settings.accent_theme)
        self.ai_mode_var.set(self.settings.local_ai_mode)
        self.logs_folder.set(self.settings.export_logs_folder)
        save_settings(self.settings)
        self.set_status("Settings reset")
        self.add_log("Settings reset to defaults")

    def open_config_note(self) -> None:
        Path("config").mkdir(exist_ok=True)
        messagebox.showinfo("Config Folder", "Settings are saved in config/settings.json inside this project folder.")
