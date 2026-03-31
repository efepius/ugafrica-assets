"""Reel preset definitions for UGAFRICA workflows.

Each preset is a dict describing how to sequence images into a CapCut draft:
- image_duration_s: seconds per image
- transition: TransitionType name and duration
- keyframes: per-image keyframe animation pattern
- intro/outro: animation types per segment
- title: optional title text config
"""

PRESETS = {
    "slideshow": {
        "description": "Clean slideshow with crossfades and subtle zoom. Great for polished, professional reels.",
        "image_duration_s": 4.0,
        "transition": {"type": "叠化", "duration_s": 0.5},
        "keyframes": {
            "pattern": "zoom_in",
            "start_scale": 1.0,
            "end_scale": 1.05,
        },
        "intro": None,
        "outro": None,
        "title": None,
    },
    "kenburns": {
        "description": "Classic Ken Burns with alternating zoom+pan directions. Cinematic documentary feel.",
        "image_duration_s": 5.0,
        "transition": {"type": "叠化", "duration_s": 0.8},
        "keyframes": {
            "pattern": "alternating",
            "patterns": [
                {"start_scale": 1.0, "end_scale": 1.15, "start_x": 0.0, "end_x": -0.1, "start_y": 0.0, "end_y": -0.05},
                {"start_scale": 1.15, "end_scale": 1.0, "start_x": -0.1, "end_x": 0.0, "start_y": -0.05, "end_y": 0.0},
                {"start_scale": 1.0, "end_scale": 1.1, "start_x": 0.0, "end_x": 0.1, "start_y": 0.0, "end_y": 0.05},
                {"start_scale": 1.1, "end_scale": 1.0, "start_x": 0.1, "end_x": 0.0, "start_y": 0.05, "end_y": 0.0},
            ],
        },
        "intro": None,
        "outro": None,
        "title": None,
    },
    "dynamic": {
        "description": "High-energy with varied animations and transitions. Perfect for social media reels.",
        "image_duration_s": 3.0,
        "transition": {
            "type": "varied",
            "options": ["Flip_Zoom", "Swirl", "Bump", "Flash", "Cube_Rotate", "Snap_Zoom"],
            "duration_s": 0.5,
        },
        "keyframes": {
            "pattern": "zoom_in",
            "start_scale": 1.0,
            "end_scale": 1.08,
        },
        "intro": {
            "type": "varied",
            "options": ["向上滑动", "放大", "渐显", "动感放大"],
            "duration_s": 0.5,
        },
        "outro": None,
        "title": {
            "enabled": True,
            "position": "first_image",
            "style": {
                "size": 12.0,
                "bold": True,
                "color": [1.0, 1.0, 1.0],
                "align": 1,
                "border_color": [0.0, 0.0, 0.0],
                "border_width": 60.0,
            },
        },
    },
    "minimal": {
        "description": "Simple and clean with long holds and soft fades. Elegant and understated.",
        "image_duration_s": 5.0,
        "transition": {"type": "叠化", "duration_s": 1.0},
        "keyframes": None,
        "intro": {"type": "渐显", "duration_s": 0.8},
        "outro": {"type": "渐隐", "duration_s": 0.8},
        "title": None,
    },
}


def get_preset(name: str) -> dict:
    """Get a preset by name. Raises KeyError if not found."""
    if name not in PRESETS:
        available = ", ".join(PRESETS.keys())
        raise KeyError(f"Unknown preset '{name}'. Available: {available}")
    return PRESETS[name]


def list_all_presets() -> list[dict]:
    """Return all presets with their names and descriptions."""
    return [
        {"name": name, "description": preset["description"]}
        for name, preset in PRESETS.items()
    ]
