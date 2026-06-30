# Packaging Mason Organizer

## Windows EXE with PyInstaller

On a Windows machine:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
pyinstaller scripts\mason_organizer_windows.spec
```

The executable will appear in `dist/Mason Organizer/`.

## Linux build

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
pyinstaller scripts/mason_organizer_linux.spec
```

## Notes

- Build Windows installers on Windows.
- Build Linux packages on Linux.
- The `.ico` file is stored in `assets/icons/mason-organizer-icon.ico`.
