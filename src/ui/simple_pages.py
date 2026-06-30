import customtkinter as ctk

from src.ui.theme import COLORS


class SimplePage(ctk.CTkFrame):
    def __init__(self, parent, title: str, subtitle: str, body: str):
        super().__init__(parent, corner_radius=22, fg_color=COLORS["background"])
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(self, text=title, font=ctk.CTkFont(size=32, weight="bold"), text_color=COLORS["text"]).grid(
            row=0, column=0, sticky="w", pady=(0, 6)
        )
        ctk.CTkLabel(self, text=subtitle, font=ctk.CTkFont(size=15), text_color=COLORS["muted"]).grid(
            row=1, column=0, sticky="w", pady=(0, 18)
        )
        card = ctk.CTkFrame(self, corner_radius=18, fg_color=COLORS["surface"])
        card.grid(row=2, column=0, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(0, weight=1)
        ctk.CTkLabel(card, text=body, justify="left", anchor="nw", text_color=COLORS["text"], font=ctk.CTkFont(size=15)).grid(
            row=0, column=0, padx=24, pady=24, sticky="nsew"
        )


class LogsPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=22, fg_color=COLORS["background"])
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(self, text="Activity Log", font=ctk.CTkFont(size=32, weight="bold"), text_color=COLORS["text"]).grid(
            row=0, column=0, sticky="w", pady=(0, 18)
        )
        self.log_box = ctk.CTkTextbox(self, fg_color=COLORS["surface"], text_color=COLORS["text"], corner_radius=18)
        self.log_box.grid(row=1, column=0, sticky="nsew")
        self.add_log("Mason Organizer started.")

    def add_log(self, message: str) -> None:
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"• {message}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")
