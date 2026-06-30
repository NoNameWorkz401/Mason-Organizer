"""Shared brand theme values for Mason Organizer."""

APP_NAME = "Mason Organizer"
VERSION = "1.0.0"

THEMES = {
    "Midnight": {
        "background": "#050B14",
        "background_2": "#07111F",
        "sidebar": "#08111E",
        "topbar": "#030812",
        "surface": "#0B1626",
        "surface_alt": "#101D30",
        "surface_light": "#14243A",
        "surface_lighter": "#1D3352",
        "primary": "#20BDF7",
        "primary_dark": "#2563EB",
        "secondary": "#6D35E8",
        "accent": "#20D0C4",
        "success": "#23E13A",
        "success_dark": "#0EA33B",
        "warning": "#F59E0B",
        "orange": "#F97316",
        "danger": "#EF4444",
        "text": "#F8FAFC",
        "muted": "#A6B3C6",
        "muted_dark": "#6F7E92",
        "border": "#22344F",
        "input": "#050C16",
        "card_border": "#1C2D46",
    },
    "Ocean": {
        "background": "#041018", "background_2": "#071C25", "sidebar": "#071722", "topbar": "#031016",
        "surface": "#0A1D29", "surface_alt": "#102B39", "surface_light": "#143B4D", "surface_lighter": "#1B5268",
        "primary": "#22D3EE", "primary_dark": "#0891B2", "secondary": "#2563EB", "accent": "#2DD4BF",
        "success": "#22C55E", "success_dark": "#16A34A", "warning": "#F59E0B", "orange": "#F97316", "danger": "#EF4444",
        "text": "#F8FAFC", "muted": "#A7C7D4", "muted_dark": "#6B8794", "border": "#235063", "input": "#031017", "card_border": "#1E4353",
    },
    "Neon": {
        "background": "#090516", "background_2": "#120A29", "sidebar": "#0E0820", "topbar": "#070311",
        "surface": "#130D2A", "surface_alt": "#1D123A", "surface_light": "#2A1C55", "surface_lighter": "#3B2875",
        "primary": "#A855F7", "primary_dark": "#7C3AED", "secondary": "#EC4899", "accent": "#22D3EE",
        "success": "#22C55E", "success_dark": "#16A34A", "warning": "#F59E0B", "orange": "#F97316", "danger": "#EF4444",
        "text": "#FAF5FF", "muted": "#C4B5FD", "muted_dark": "#8370B2", "border": "#422A78", "input": "#080411", "card_border": "#35235F",
    },
    "Emerald": {
        "background": "#03130D", "background_2": "#071C14", "sidebar": "#061811", "topbar": "#020D09",
        "surface": "#0A2017", "surface_alt": "#0E2B20", "surface_light": "#164333", "surface_lighter": "#1D5C45",
        "primary": "#34D399", "primary_dark": "#059669", "secondary": "#14B8A6", "accent": "#A3E635",
        "success": "#22C55E", "success_dark": "#16A34A", "warning": "#F59E0B", "orange": "#F97316", "danger": "#EF4444",
        "text": "#F0FDF4", "muted": "#A7F3D0", "muted_dark": "#669B82", "border": "#225845", "input": "#020D09", "card_border": "#1C4939",
    },
    "Sunset": {
        "background": "#160904", "background_2": "#251108", "sidebar": "#1C0B05", "topbar": "#0F0502",
        "surface": "#281209", "surface_alt": "#391A0B", "surface_light": "#552811", "surface_lighter": "#753916",
        "primary": "#FB923C", "primary_dark": "#EA580C", "secondary": "#F43F5E", "accent": "#FACC15",
        "success": "#22C55E", "success_dark": "#16A34A", "warning": "#F59E0B", "orange": "#F97316", "danger": "#EF4444",
        "text": "#FFF7ED", "muted": "#FDBA74", "muted_dark": "#9A6B45", "border": "#6B3215", "input": "#100602", "card_border": "#51250F",
    },
    "Crimson": {
        "background": "#140507", "background_2": "#22090D", "sidebar": "#1B070A", "topbar": "#0D0204",
        "surface": "#260B10", "surface_alt": "#351019", "surface_light": "#4D1824", "surface_lighter": "#6C2434",
        "primary": "#FB7185", "primary_dark": "#E11D48", "secondary": "#DC2626", "accent": "#F97316",
        "success": "#22C55E", "success_dark": "#16A34A", "warning": "#F59E0B", "orange": "#F97316", "danger": "#EF4444",
        "text": "#FFF1F2", "muted": "#FDA4AF", "muted_dark": "#9C6470", "border": "#672334", "input": "#0E0305", "card_border": "#52202B",
    },
    "Graphite": {
        "background": "#09090B", "background_2": "#111113", "sidebar": "#111113", "topbar": "#050506",
        "surface": "#18181B", "surface_alt": "#202024", "surface_light": "#27272A", "surface_lighter": "#3F3F46",
        "primary": "#A1A1AA", "primary_dark": "#52525B", "secondary": "#71717A", "accent": "#E4E4E7",
        "success": "#22C55E", "success_dark": "#16A34A", "warning": "#F59E0B", "orange": "#F97316", "danger": "#EF4444",
        "text": "#FAFAFA", "muted": "#A1A1AA", "muted_dark": "#71717A", "border": "#3F3F46", "input": "#09090B", "card_border": "#303034",
    },
}

COLORS = THEMES["Midnight"].copy()
ACCENT_THEMES = {name: {"primary": values["primary"], "primary_dark": values["primary_dark"], "secondary": values["secondary"]} for name, values in THEMES.items()}

CATEGORY_COLORS = {
    "Images": "#1677FF", "Documents": "#22C55E", "Videos": "#F59E0B", "Audio": "#F97316",
    "Archives": "#6D35E8", "Code": "#20BDF7", "Other": "#64748B", "Others": "#64748B",
}

FONTS = {
    "title": ("Arial", 30, "bold"), "subtitle": ("Arial", 15), "section": ("Arial", 20, "bold"),
    "card_title": ("Arial", 14), "card_value": ("Arial", 26, "bold"),
}

def apply_theme(theme_name: str) -> str:
    """Mutate the shared COLORS dictionary so newly-created widgets use the selected theme."""
    selected = theme_name if theme_name in THEMES else "Midnight"
    COLORS.clear()
    COLORS.update(THEMES[selected])
    return selected
