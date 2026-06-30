import customtkinter as ctk

from src.ui.theme import COLORS


class StatusBar(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, height=34, corner_radius=0, fg_color=COLORS["background"])
        self.grid_columnconfigure(1, weight=1)

        self.status_label = ctk.CTkLabel(self, text="Status: Ready", anchor="w", text_color=COLORS["muted"])
        self.status_label.grid(row=0, column=0, padx=28, pady=6, sticky="w")

        ctk.CTkLabel(
            self,
            text="All processing is 100% local. Your data never leaves your device.",
            text_color=COLORS["muted"],
        ).grid(row=0, column=1, pady=6)

        ctk.CTkLabel(self, text="🛡  Secure & Private", text_color=COLORS["text"]).grid(
            row=0, column=2, padx=28, pady=6, sticky="e"
        )

    def set_status(self, message: str) -> None:
        self.status_label.configure(text=f"Status: {message}")
