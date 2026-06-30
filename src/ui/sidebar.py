import customtkinter as ctk

from src.ui.theme import COLORS, VERSION


class Sidebar(ctk.CTkFrame):
    def __init__(self, parent, on_navigation):
        super().__init__(parent, width=246, corner_radius=0, fg_color=COLORS["sidebar"])
        self.on_navigation = on_navigation
        self.buttons: dict[str, ctk.CTkButton] = {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(13, weight=1)

        # Text-based logo so the project stays lightweight and portable.
        ctk.CTkLabel(
            self,
            text="▱M",
            font=ctk.CTkFont(family="Arial", size=64, weight="bold"),
            text_color=COLORS["primary"],
        ).grid(row=0, column=0, padx=18, pady=(24, 0), sticky="w")
        ctk.CTkLabel(
            self,
            text="M A S O N",
            font=ctk.CTkFont(family="Arial", size=28, weight="bold"),
            text_color=COLORS["text"],
        ).grid(row=1, column=0, padx=22, sticky="w")
        ctk.CTkLabel(
            self,
            text="O R G A N I Z E R",
            font=ctk.CTkFont(family="Arial", size=15, weight="bold"),
            text_color=COLORS["primary"],
        ).grid(row=2, column=0, padx=24, sticky="w")
        ctk.CTkLabel(
            self,
            text="Organize. Optimize. Simplify.",
            text_color=COLORS["text"],
            anchor="w",
        ).grid(row=3, column=0, padx=24, pady=(8, 22), sticky="ew")

        nav_items = [
            ("dashboard", "⌂", "Dashboard"),
            ("search", "⌕", "Search"),
            ("organizer", "□", "Organizer"),
            ("analytics", "◔", "Analytics"),
            ("ai", "✧", "AI Assistant"),
            ("chat", "▱", "AI Chat Assistant"),
            ("settings", "⚙", "Settings"),
            ("logs", "☷", "Logs"),
            ("about", "ⓘ", "About"),
        ]

        for row, (key, icon, label) in enumerate(nav_items, start=4):
            button = ctk.CTkButton(
                self,
                text=f"{icon}   {label}",
                height=48,
                corner_radius=9,
                anchor="w",
                font=ctk.CTkFont(family="Arial", size=16),
                fg_color="transparent",
                hover_color=COLORS["surface_light"],
                text_color=COLORS["text"],
                command=lambda page=key: self.navigate(page),
            )
            button.grid(row=row, column=0, padx=16, pady=4, sticky="ew")
            self.buttons[key] = button

        pro_card = ctk.CTkFrame(self, corner_radius=12, fg_color=COLORS["input"], border_width=1, border_color=COLORS["secondary"])
        pro_card.grid(row=13, column=0, padx=16, pady=(12, 10), sticky="ew")
        ctk.CTkLabel(pro_card, text="♛  Mason Pro", text_color="#E879F9", font=ctk.CTkFont(size=15, weight="bold")).pack(
            anchor="w", padx=16, pady=(12, 0)
        )
        ctk.CTkLabel(pro_card, text="Advanced features coming soon", text_color=COLORS["muted"], font=ctk.CTkFont(size=12)).pack(
            anchor="w", padx=16, pady=(0, 12)
        )

        privacy = ctk.CTkFrame(self, corner_radius=14, fg_color=COLORS["surface"], border_width=1, border_color=COLORS["border"])
        privacy.grid(row=14, column=0, padx=16, pady=(0, 12), sticky="ew")
        ctk.CTkLabel(privacy, text="🛡", font=ctk.CTkFont(size=34), text_color=COLORS["primary"]).grid(row=0, column=0, padx=14, pady=14)
        ctk.CTkLabel(privacy, text="Your files.\nYour data.\nAlways private.", justify="left", text_color=COLORS["text"]).grid(
            row=0, column=1, padx=(0, 12), pady=14, sticky="w"
        )
        ctk.CTkLabel(privacy, text="100% Local Processing", text_color=COLORS["success"]).grid(
            row=1, column=0, columnspan=2, padx=14, pady=(0, 12), sticky="w"
        )

        footer = ctk.CTkLabel(self, text=f"Version {VERSION}", text_color=COLORS["muted_dark"])
        footer.grid(row=15, column=0, padx=24, pady=(0, 18), sticky="w")
        self.set_active("dashboard")

    def navigate(self, page_name: str) -> None:
        self.set_active(page_name)
        self.on_navigation(page_name)

    def set_active(self, page_name: str) -> None:
        for key, button in self.buttons.items():
            if key == page_name:
                button.configure(fg_color=COLORS["primary_dark"], hover_color=COLORS["secondary"])
            else:
                button.configure(fg_color="transparent", hover_color=COLORS["surface_light"])
