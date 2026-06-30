# Contributing

Thanks for your interest in Mason Organizer.

## Development Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
python main.py
```

## Rules

- Keep file operations safe by default.
- Do not delete user files automatically.
- Keep AI features local-first unless the user explicitly chooses an external provider.
- Test organizer changes on copied folders before release.
