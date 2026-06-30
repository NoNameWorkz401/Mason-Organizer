from __future__ import annotations

import platform
import sys
import webbrowser
from datetime import datetime

import customtkinter as ctk

from src.ui.theme import APP_NAME, COLORS, VERSION


class AboutPage(ctk.CTkFrame):
    """Polished About page for Mason Organizer."""

    def __init__(self, parent, set_status, add_log):
        super().__init__(parent, fg_color=COLORS["background"])
        self.set_status = set_status
        self.add_log = add_log

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        hero = ctk.CTkFrame(
            scroll,
            corner_radius=24,
            fg_color=COLORS["surface"],
            border_width=1,
            border_color=COLORS["card_border"],
        )
        hero.grid(row=0, column=0, padx=22, pady=(22, 16), sticky="ew")
        hero.grid_columnconfigure(1, weight=1)

        logo = ctk.CTkFrame(hero, width=104, height=104, corner_radius=28, fg_color=COLORS["primary_dark"])
        logo.grid(row=0, column=0, rowspan=3, padx=28, pady=28, sticky="n")
        logo.grid_propagate(False)
        ctk.CTkLabel(
            logo,
            text="▱M",
            font=ctk.CTkFont(family="Arial", size=42, weight="bold"),
            text_color=COLORS["text"],
        ).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            hero,
            text=APP_NAME,
            font=ctk.CTkFont(family="Arial", size=36, weight="bold"),
            text_color=COLORS["text"],
        ).grid(row=0, column=1, padx=(0, 24), pady=(30, 0), sticky="w")

        ctk.CTkLabel(
            hero,
            text="AI-Powered File Management",
            font=ctk.CTkFont(family="Arial", size=18, weight="bold"),
            text_color=COLORS["primary"],
        ).grid(row=1, column=1, padx=(0, 24), pady=(4, 0), sticky="w")

        ctk.CTkLabel(
            hero,
            text=f"Version {VERSION}  •  Built with Python & CustomTkinter  •  Local-first by default",
            text_color=COLORS["muted"],
        ).grid(row=2, column=1, padx=(0, 24), pady=(6, 26), sticky="w")

        mission = self._section(scroll, 1, "Mission")
        ctk.CTkLabel(
            mission,
            text=(
                "Mason Organizer helps users safely organize, analyze, and understand their files using a modern "
                "desktop interface and privacy-focused AI assistance. The goal is simple: spend less time "
                "cleaning folders and more time creating."
            ),
            text_color=COLORS["text"],
            wraplength=860,
            justify="left",
        ).grid(row=1, column=0, padx=20, pady=(0, 18), sticky="w")

        info_grid = ctk.CTkFrame(scroll, fg_color="transparent")
        info_grid.grid(row=2, column=0, padx=22, pady=0, sticky="ew")
        info_grid.grid_columnconfigure((0, 1), weight=1)

        details = self._small_card(info_grid, 0, 0, "Project Details")
        self._detail(details, 0, "Developer", "Dylan Fortin")
        self._detail(details, 1, "AI Development Assistant", "Mason")
        self._detail(details, 2, "License", "MIT License")
        self._detail(details, 3, "Release", str(VERSION))

        system = self._small_card(info_grid, 0, 1, "System Info")
        self._detail(system, 0, "Operating System", f"{platform.system()} {platform.release()}")
        self._detail(system, 1, "Python", sys.version.split()[0])
        self._detail(system, 2, "Machine", platform.machine())
        self._detail(system, 3, "Build Date", datetime.now().strftime("%Y-%m-%d"))

        tech = self._section(scroll, 3, "Built With")
        badges = ctk.CTkFrame(tech, fg_color="transparent")
        badges.grid(row=1, column=0, padx=20, pady=(0, 18), sticky="w")
        for index, label in enumerate(["Python", "CustomTkinter", "PyInstaller", "Local AI Rules", "SHA-256"]):
            ctk.CTkLabel(
                badges,
                text=label,
                fg_color=COLORS["surface_light"],
                text_color=COLORS["text"],
                corner_radius=16,
                padx=14,
                pady=8,
            ).grid(row=0, column=index, padx=(0, 10), pady=4)

        actions = ctk.CTkFrame(scroll, fg_color="transparent")
        actions.grid(row=4, column=0, padx=22, pady=(4, 22), sticky="ew")
        ctk.CTkButton(actions, text="Open GitHub", command=self._open_github).grid(row=0, column=0, padx=(0, 12), pady=8)
        ctk.CTkButton(actions, text="Documentation", command=self._docs).grid(row=0, column=1, padx=(0, 12), pady=8)
        ctk.CTkButton(actions, text="Check for Updates", command=self._updates).grid(row=0, column=2, padx=(0, 12), pady=8)

        ctk.CTkLabel(
            scroll,
            text="Thank you for using Mason Organizer.",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["primary"],
        ).grid(row=5, column=0, padx=22, pady=(0, 28), sticky="w")

    def _section(self, parent, row: int, title: str) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(parent, corner_radius=18, fg_color=COLORS["surface"], border_width=1, border_color=COLORS["card_border"])
        frame.grid(row=row, column=0, padx=22, pady=(0, 16), sticky="ew")
        frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(size=20, weight="bold"), text_color=COLORS["text"]).grid(
            row=0, column=0, padx=20, pady=(18, 10), sticky="w"
        )
        return frame

    def _small_card(self, parent, row: int, column: int, title: str) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(parent, corner_radius=18, fg_color=COLORS["surface"], border_width=1, border_color=COLORS["card_border"])
        frame.grid(row=row, column=column, padx=(0, 10) if column == 0 else (10, 0), pady=(0, 16), sticky="nsew")
        frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(size=18, weight="bold"), text_color=COLORS["text"]).grid(
            row=0, column=0, columnspan=2, padx=20, pady=(18, 10), sticky="w"
        )
        return frame

    def _detail(self, parent, row: int, label: str, value: str) -> None:
        ctk.CTkLabel(parent, text=label, text_color=COLORS["muted"], anchor="w").grid(
            row=row + 1, column=0, padx=20, pady=5, sticky="w"
        )
        ctk.CTkLabel(parent, text=value, text_color=COLORS["text"], anchor="w").grid(
            row=row + 1, column=1, padx=20, pady=5, sticky="ew"
        )

    def _open_github(self) -> None:
        webbrowser.open("https://github.com/nonameworkz/Mason-Organizer")
        self.set_status("Opening GitHub page")
        self.add_log("Opened GitHub project link")

    def _docs(self) -> None:
        self.set_status("Documentation is included in the project README")
        self.add_log("Viewed documentation shortcut")

    def _updates(self) -> None:
        self.set_status("You are running the packaged v1.0 build")
        self.add_log("Checked for updates")
