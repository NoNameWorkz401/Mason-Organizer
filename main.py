"""Entry point for Mason Organizer."""

from src.ui.app import MasonOrganizerApp


def main() -> None:
    app = MasonOrganizerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
