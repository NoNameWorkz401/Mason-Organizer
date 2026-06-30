from __future__ import annotations

import customtkinter as ctk

from src.core.chat_assistant import answer_question
from src.ui.theme import COLORS


class ChatAssistantPage(ctk.CTkFrame):
    def __init__(self, parent, set_status, add_log):
        super().__init__(parent, corner_radius=22, fg_color=COLORS["background"])
        self.set_status = set_status
        self.add_log = add_log
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(self, text="AI Chat Assistant", font=ctk.CTkFont(size=32, weight="bold"), text_color=COLORS["text"]).grid(row=0, column=0, sticky="w", pady=(0, 6))
        ctk.CTkLabel(self, text="Ask questions about the app, safe workflow, and what each section does. Runs locally with rule-based answers.", font=ctk.CTkFont(size=15), text_color=COLORS["muted"]).grid(row=1, column=0, sticky="w", pady=(0, 18))

        quick = ctk.CTkFrame(self, fg_color="transparent")
        quick.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        prompts = ["Explain Dashboard", "How do I use Organizer?", "Safest workflow", "Explain duplicate finder"]
        for index, prompt in enumerate(prompts):
            ctk.CTkButton(quick, text=prompt, height=36, corner_radius=12, fg_color=COLORS["surface_light"], hover_color=COLORS["surface_lighter"], command=lambda p=prompt: self.ask(p)).grid(row=0, column=index, padx=(0, 10))

        self.chat = ctk.CTkTextbox(self, fg_color=COLORS["surface"], text_color=COLORS["text"], corner_radius=18, wrap="word")
        self.chat.grid(row=3, column=0, sticky="nsew", pady=(0, 14))
        self.chat.insert("end", "Mason AI: Ask me how to use Mason Organizer.\n\n")
        self.chat.configure(state="disabled")

        entry_box = ctk.CTkFrame(self, corner_radius=18, fg_color=COLORS["surface"])
        entry_box.grid(row=4, column=0, sticky="ew")
        entry_box.grid_columnconfigure(0, weight=1)
        self.entry = ctk.CTkEntry(entry_box, placeholder_text="Ask about Dashboard, Organizer, Analytics, Search, AI, Logs, Settings...", height=44)
        self.entry.grid(row=0, column=0, padx=14, pady=14, sticky="ew")
        self.entry.bind("<Return>", lambda _event: self.send())
        ctk.CTkButton(entry_box, text="Send", width=110, height=44, corner_radius=12, command=self.send).grid(row=0, column=1, padx=(0, 14), pady=14)

    def _append(self, speaker: str, text: str) -> None:
        self.chat.configure(state="normal")
        self.chat.insert("end", f"{speaker}: {text}\n\n")
        self.chat.see("end")
        self.chat.configure(state="disabled")

    def ask(self, prompt: str) -> None:
        self.entry.delete(0, "end")
        self.entry.insert(0, prompt)
        self.send()

    def send(self) -> None:
        question = self.entry.get().strip()
        if not question:
            return
        self.entry.delete(0, "end")
        self._append("You", question)
        answer = answer_question(question)
        self._append("Mason AI", answer)
        self.set_status("AI Chat answered question")
        self.add_log(f"AI Chat answered: {question}")
