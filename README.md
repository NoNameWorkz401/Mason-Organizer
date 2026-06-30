# Mason Organizer

**AI-Powered File Management**

Mason Organizer is a modern desktop application for safely organizing, analyzing, and understanding your files. It combines a polished CustomTkinter interface, safe file-management workflows, duplicate detection, search, reports, themes, and a local-first AI assistant.

![Mason Organizer Logo](assets/logo/mason-organizer-logo.png)

## Features

- Modern dark UI with multiple color themes
- Folder scanning with live progress
- File category breakdowns
- Safe organization preview
- Organize files by category
- Undo last organization job
- Duplicate file finder using SHA-256 hashes
- Search page with file preview and report export
- Analytics page
- Local-first Mason AI assistant
- AI chat assistant for explaining app sections and workflows
- Settings page with saved preferences
- Branded splash screen
- About page with app/system information
- GitHub-ready project structure

## Safety First

Mason Organizer is designed to avoid destructive actions.

- It previews organization actions before moving files.
- It supports undo for organization jobs.
- Duplicate detection reports duplicates but does not delete them automatically.
- AI features are local/rule-based by default.

Always test on a copied folder before using any file-management tool on important files.

## Run from Source

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

On Ubuntu, Tkinter may need to be installed separately:

```bash
sudo apt install python3-tk
```

## Developer Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
python main.py
```

## Build an EXE

See [`docs/PACKAGING.md`](docs/PACKAGING.md).

Quick Windows build:

```powershell
pip install -r requirements-dev.txt
pyinstaller scripts\mason_organizer_windows.spec
```

## Project Structure

```text
Mason-Organizer/
├── assets/
│   ├── icons/
│   └── logo/
├── docs/
├── scripts/
├── src/
│   ├── core/
│   └── ui/
├── tests/
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── main.py
├── requirements.txt
└── requirements-dev.txt
```

## Roadmap

- Windows installer
- Linux AppImage / `.deb`
- Custom organization rules
- Workspaces
- Optional Ollama integration
- Optional cloud AI provider support
- Plugin system

## Credits

Developer: **Dylan Fortin**  
AI Development Assistant: **Mason**

Built with Python and CustomTkinter.

## License

MIT License
