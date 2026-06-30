from __future__ import annotations

from pathlib import Path

import customtkinter as ctk

from src.core.settings import load_settings
from src.ui.about_page import AboutPage
from src.ui.ai_page import AIAssistantPage
from src.ui.analytics_page import AnalyticsPage
from src.ui.chat_page import ChatAssistantPage
from src.ui.dashboard import Dashboard
from src.ui.organizer_page import OrganizerPage
from src.ui.search_page import SearchPage
from src.ui.settings_page import SettingsPage
from src.ui.sidebar import Sidebar
from src.ui.simple_pages import LogsPage
from src.ui.statusbar import StatusBar
from src.ui.theme import APP_NAME, COLORS, VERSION, apply_theme


class TopBar(ctk.CTkFrame):
    """Simple app header that gives the project a desktop-software feel."""

    def __init__(self, parent):
        super().__init__(parent, height=58, corner_radius=0, fg_color=COLORS["topbar"])
        self.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self, text="☰", font=ctk.CTkFont(size=24), text_color=COLORS["text"]).grid(
            row=0, column=0, padx=(28, 18), pady=14
        )
        ctk.CTkLabel(
            self,
            text=APP_NAME,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text"],
        ).grid(row=0, column=1, sticky="w")
        ctk.CTkLabel(self, text=str(VERSION), text_color=COLORS["primary"]).grid(
            row=0, column=1, padx=(170, 0), sticky="w"
        )

        for col, icon in enumerate(["🌙", "🔒", "●"], start=2):
            ctk.CTkLabel(self, text=icon, font=ctk.CTkFont(size=18), text_color=COLORS["muted"]).grid(
                row=0, column=col, padx=12
            )


class MasonOrganizerApp(ctk.CTk):
    def __init__(self):
        settings = load_settings()
        apply_theme(settings.accent_theme)

        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title(APP_NAME)
        self.geometry("1360x820")
        self.minsize(1080, 680)
        self.configure(fg_color=COLORS["background"])
        self._set_window_icon()
        self.withdraw()
        self.after(80, self._show_splash)

        self.logs_page: LogsPage | None = None
        self.pages: dict[str, ctk.CTkFrame] = {}
        self._build_shell()

    def _set_window_icon(self) -> None:
        """Apply bundled app icon when the platform supports it."""
        icon_path = Path(__file__).resolve().parents[2] / "assets" / "icons" / "mason-organizer-icon.ico"
        if icon_path.exists():
            try:
                self.iconbitmap(str(icon_path))
            except Exception:
                # Linux desktops often ignore .ico through Tk. Packaging scripts still use it.
                pass

    def _show_splash(self) -> None:
        """Show a short branded splash screen before the main window appears."""
        splash = ctk.CTkToplevel(self)
        splash.title(APP_NAME)
        splash.geometry("520x330")
        splash.resizable(False, False)
        splash.configure(fg_color=COLORS["background"])
        splash.overrideredirect(True)

        splash.update_idletasks()
        width = 520
        height = 330
        x = (splash.winfo_screenwidth() // 2) - (width // 2)
        y = (splash.winfo_screenheight() // 2) - (height // 2)
        splash.geometry(f"{width}x{height}+{x}+{y}")

        card = ctk.CTkFrame(
            splash,
            corner_radius=26,
            fg_color=COLORS["surface"],
            border_width=1,
            border_color=COLORS["primary"],
        )
        card.pack(fill="both", expand=True, padx=18, pady=18)

        logo = ctk.CTkFrame(card, width=88, height=88, corner_radius=24, fg_color=COLORS["primary_dark"])
        logo.pack(pady=(34, 12))
        logo.pack_propagate(False)
        ctk.CTkLabel(
            logo,
            text="▱M",
            font=ctk.CTkFont(size=34, weight="bold"),
            text_color=COLORS["text"],
        ).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            card,
            text=APP_NAME,
            font=ctk.CTkFont(size=30, weight="bold"),
            text_color=COLORS["text"],
        ).pack()
        ctk.CTkLabel(
            card,
            text="AI-Powered File Management",
            text_color=COLORS["primary"],
            font=ctk.CTkFont(size=15, weight="bold"),
        ).pack(pady=(3, 6))
        ctk.CTkLabel(card, text=f"Version {VERSION}", text_color=COLORS["muted"]).pack()

        progress = ctk.CTkProgressBar(card, width=330, progress_color=COLORS["primary"])
        progress.pack(pady=(22, 8))
        progress.set(0.78)
        ctk.CTkLabel(card, text="Loading workspace...", text_color=COLORS["muted"]).pack()

        def finish() -> None:
            splash.destroy()
            self.deiconify()
            self.lift()
            self.focus_force()

        splash.after(1500, finish)

    def _clear_shell(self) -> None:
        for child in self.winfo_children():
            child.destroy()

    def _build_shell(self) -> None:
        self._clear_shell()
        self.configure(fg_color=COLORS["background"])

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.sidebar = Sidebar(self, self.show_page)
        self.sidebar.grid(row=0, column=0, rowspan=3, sticky="nsew")

        self.topbar = TopBar(self)
        self.topbar.grid(row=0, column=1, sticky="ew")

        self.content = ctk.CTkFrame(self, fg_color=COLORS["background"])
        self.content.grid(row=1, column=1, sticky="nsew", padx=22, pady=18)
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        self.statusbar = StatusBar(self)
        self.statusbar.grid(row=2, column=1, sticky="ew")

        self.logs_page = LogsPage(self.content)
        self.pages = {
            "dashboard": Dashboard(self.content, self.statusbar.set_status, self.add_log, self.show_page),
            "search": SearchPage(self.content, self.statusbar.set_status, self.add_log),
            "organizer": OrganizerPage(self.content, self.statusbar.set_status, self.add_log),
            "analytics": AnalyticsPage(self.content, self.statusbar.set_status, self.add_log),
            "ai": AIAssistantPage(self.content, self.statusbar.set_status, self.add_log),
            "chat": ChatAssistantPage(self.content, self.statusbar.set_status, self.add_log),
            "logs": self.logs_page,
            "settings": SettingsPage(self.content, self.statusbar.set_status, self.add_log, self.apply_new_theme),
            "about": AboutPage(self.content, self.statusbar.set_status, self.add_log),
        }

        for page in self.pages.values():
            page.grid(row=0, column=0, sticky="nsew")

        self.show_page("dashboard")

    def apply_new_theme(self, theme_name: str) -> None:
        """Apply theme immediately by rebuilding the UI with the new shared color palette."""
        active = apply_theme(theme_name)
        self._build_shell()
        self.show_page("settings")
        self.statusbar.set_status(f"Theme applied: {active}")
        self.add_log(f"Theme changed to {active}")

    def show_page(self, page_name: str) -> None:
        page = self.pages[page_name]
        page.tkraise()
        self.sidebar.set_active(page_name)
        self.statusbar.set_status(f"Viewing {page_name.replace('_', ' ').title()}")

    def add_log(self, message: str) -> None:
        if self.logs_page is not None:
            self.logs_page.add_log(message)
        dashboard = getattr(self, "pages", {}).get("dashboard")
        if dashboard and hasattr(dashboard, "add_activity"):
            dashboard.add_activity(message)
