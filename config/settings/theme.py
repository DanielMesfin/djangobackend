from typing import Dict

# Centralized theme and color settings
THEME_COLORS: Dict[str, str] = {
    "brand_colour": "navbar-primary",
    "accent": "accent-primary",
    "navbar": "navbar-dark",
    "sidebar": "sidebar-dark-primary",
}

BUTTON_CLASSES: Dict[str, str] = {
    "primary": "btn-primary",
    "secondary": "btn-secondary",
    "info": "btn-info",
    "warning": "btn-warning",
    "danger": "btn-danger",
    "success": "btn-success",
}

# Exported Jazzmin UI tweaks built from the central colors
JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": THEME_COLORS["brand_colour"],
    "accent": THEME_COLORS["accent"],
    "navbar": THEME_COLORS["navbar"],
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": False,
    "sidebar": THEME_COLORS["sidebar"],
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "dark_mode_theme": None,
    "button_classes": BUTTON_CLASSES,
}
