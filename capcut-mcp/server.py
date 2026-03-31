#!/usr/bin/env python3
"""CapCut Desktop MCP Server — Full video editing toolkit for UGAFRICA reels.

Run: python3 server.py
Transport: stdio (for Claude Desktop / Claude Code)
"""

import json
import sys
import os

# Add this directory to path so imports work
sys.path.insert(0, os.path.dirname(__file__))

from mcp.server.fastmcp import FastMCP
from draft_manager import DraftManager
from presets import list_all_presets
from plugins import load_plugins

# ── Initialize ───────────────────────────────────────────────────────

server = FastMCP(
    "capcut",
    instructions=(
        "CapCut Desktop MCP Server for UGAFRICA reel production. "
        "Create and edit CapCut video projects programmatically. "
        "Workflow: create_draft → add media/text/effects → save_draft → open in CapCut to render. "
        "Use build_reel for one-shot reel creation from project images with presets."
    ),
)

dm = DraftManager()


# ── Draft Lifecycle Tools ────────────────────────────────────────────

@server.tool()
async def create_draft(
    name: str,
    width: int = 1080,
    height: int = 1920,
    fps: int = 30,
) -> str:
    """Create a new CapCut project draft.

    Defaults to 1080x1920 (vertical reel) at 30fps.
    This becomes the active draft for all subsequent operations.

    Args:
        name: Draft name (shown in CapCut)
        width: Video width in pixels (default 1080)
        height: Video height in pixels (default 1920 for vertical)
        fps: Frames per second (default 30)
    """
    result = dm.create_draft(name, width, height, fps)
    return json.dumps(result)


@server.tool()
async def open_draft(name: str) -> str:
    """Open an existing CapCut draft for editing.

    Loads the draft in template mode so you can modify tracks, segments,
    and materials. Use list_drafts to see available drafts.

    Args:
        name: Name of the draft to open
    """
    result = dm.open_draft(name)
    return json.dumps(result)


@server.tool()
async def save_draft() -> str:
    """Save the active draft to CapCut's project directory.

    After saving, open CapCut Desktop and the project will appear
    in your drafts list, ready to preview and export.
    """
    result = dm.save_draft()
    return json.dumps(result)


@server.tool()
async def list_drafts() -> str:
    """List all CapCut drafts in the configured drafts directory.

    Returns draft names that can be opened with open_draft.
    """
    result = dm.list_drafts()
    return json.dumps(result)


@server.tool()
async def get_draft_info() -> str:
    """Get metadata about the active draft.

    Returns dimensions, fps, duration, and track/segment counts.
    Useful for understanding the current state before making changes.
    """
    result = dm.get_draft_info()
    return json.dumps(result)


@server.tool()
async def duplicate_draft(source_name: str, new_name: str) -> str:
    """Clone an existing draft as a starting point for a new project.

    The cloned draft becomes the active draft.

    Args:
        source_name: Name of the draft to clone
        new_name: Name for the new draft
    """
    result = dm.duplicate_draft(source_name, new_name)
    return json.dumps(result)


# ── Media Tools ──────────────────────────────────────────────────────

@server.tool()
async def add_video(
    path: str,
    start_s: float = 0,
    duration_s: float = 5,
    speed: float = 1.0,
    volume: float = 1.0,
    scale: float = 1.0,
    position_x: float = 0,
    position_y: float = 0,
    rotation: float = 0,
    opacity: float = 1.0,
    track_name: str = "",
) -> str:
    """Add a video clip to the timeline.

    Args:
        path: Absolute path to the video file (MP4, MOV, AVI)
        start_s: Start time on timeline in seconds
        duration_s: Duration in seconds
        speed: Playback speed (0.25 to 4.0, default 1.0)
        volume: Volume level (0.0 to 1.0+, default 1.0)
        scale: Scale factor (1.0 = original size)
        position_x: Horizontal position (-1.0 to 1.0, 0 = center)
        position_y: Vertical position (-1.0 to 1.0, 0 = center)
        rotation: Rotation in degrees
        opacity: Opacity (0.0 to 1.0)
        track_name: Target track name (auto-created if empty)
    """
    result = dm.add_video(path, start_s, duration_s, speed, volume,
                          scale, position_x, position_y, rotation, opacity,
                          track_name or None)
    return json.dumps(result)


@server.tool()
async def add_image(
    path: str,
    start_s: float = 0,
    duration_s: float = 4,
    scale: float = 1.0,
    position_x: float = 0,
    position_y: float = 0,
    rotation: float = 0,
    opacity: float = 1.0,
    track_name: str = "",
) -> str:
    """Add an image to the timeline.

    Supports PNG, JPG, GIF. Images are placed as video segments with
    a fixed duration. Great for slideshows and reel backgrounds.

    Args:
        path: Absolute path to the image file
        start_s: Start time on timeline in seconds
        duration_s: How long the image is shown in seconds
        scale: Scale factor (1.0 = original, 1.5 = 150%)
        position_x: Horizontal position (-1.0 to 1.0, 0 = center)
        position_y: Vertical position (-1.0 to 1.0, 0 = center)
        rotation: Rotation in degrees
        opacity: Opacity (0.0 to 1.0)
        track_name: Target track name (auto-created if empty)
    """
    result = dm.add_image(path, start_s, duration_s, scale, position_x,
                          position_y, rotation, opacity, track_name or None)
    return json.dumps(result)


@server.tool()
async def add_audio(
    path: str,
    start_s: float = 0,
    duration_s: float = 0,
    volume: float = 1.0,
    fade_in_s: float = 0,
    fade_out_s: float = 0,
    track_name: str = "",
) -> str:
    """Add an audio track (music, voiceover, sound effects).

    Supports MP3, WAV, and other common audio formats.
    Perfect for adding FL Studio exports, background music, or voiceovers.

    Args:
        path: Absolute path to the audio file
        start_s: Start time on timeline in seconds
        duration_s: Duration in seconds (0 = full audio length)
        volume: Volume level (0.0 to 1.0+, default 1.0)
        fade_in_s: Fade in duration in seconds (0 = no fade)
        fade_out_s: Fade out duration in seconds (0 = no fade)
        track_name: Target track name (auto-created if empty)
    """
    result = dm.add_audio(path, start_s, duration_s or None, volume,
                          fade_in_s, fade_out_s, track_name or None)
    return json.dumps(result)


# ── Text & Subtitles ─────────────────────────────────────────────────

@server.tool()
async def add_text(
    content: str,
    start_s: float = 0,
    duration_s: float = 3,
    font_size: float = 8.0,
    color: str = "1.0,1.0,1.0",
    bold: bool = False,
    italic: bool = False,
    align: int = 1,
    border_color: str = "",
    border_width: float = 0,
    bg_color: str = "",
    bg_alpha: float = 0.7,
    position_x: float = 0,
    position_y: float = 0,
    scale: float = 1.0,
    rotation: float = 0,
    track_name: str = "",
) -> str:
    """Add a text overlay to the timeline.

    Full styling: font size, color, bold/italic, text alignment,
    border (outline), background box, position, and timing.

    Args:
        content: The text to display
        start_s: Start time in seconds
        duration_s: Duration in seconds
        font_size: Font size (default 8.0, range ~4-20)
        color: RGB color as comma-separated floats "R,G,B" (0-1 range, default "1.0,1.0,1.0" = white)
        bold: Bold text
        italic: Italic text
        align: Text alignment (0=left, 1=center, 2=right)
        border_color: Outline color as "R,G,B" (empty = no border)
        border_width: Outline width (0-100, default 0 = no border)
        bg_color: Background box hex color like "#000000" (empty = no background)
        bg_alpha: Background opacity (0-1)
        position_x: Horizontal position (-1.0 to 1.0, 0 = center)
        position_y: Vertical position (-1.0 to 1.0, 0 = center, -0.7 = near bottom)
        scale: Scale factor
        rotation: Rotation in degrees
        track_name: Target track name (auto-created if empty)
    """
    color_list = [float(x.strip()) for x in color.split(",")]
    border_list = [float(x.strip()) for x in border_color.split(",")] if border_color else None
    result = dm.add_text(content, start_s, duration_s, font_size, color_list,
                         bold, italic, align, border_list, border_width,
                         bg_color, bg_alpha, position_x, position_y, scale,
                         rotation, track_name or None)
    return json.dumps(result)


@server.tool()
async def import_subtitles(
    srt_path: str,
    font_size: float = 6.0,
    color: str = "1.0,1.0,1.0",
    bold: bool = True,
    track_name: str = "",
) -> str:
    """Import an .srt subtitle file as timed text segments.

    Each subtitle entry becomes a text segment on the timeline
    with proper start/end timing.

    Args:
        srt_path: Path to the .srt subtitle file
        font_size: Font size for subtitles (default 6.0)
        color: RGB color as "R,G,B" (default white)
        bold: Bold text (default True)
        track_name: Target track name (auto-created if empty)
    """
    color_list = [float(x.strip()) for x in color.split(",")]
    result = dm.import_subtitles(srt_path, track_name or None, font_size, color_list, bold)
    return json.dumps(result)


# ── Effects & Style ──────────────────────────────────────────────────

@server.tool()
async def add_animation(
    track_name: str,
    segment_index: int,
    animation_type: str,
    category: str = "intro",
    duration_s: float = 0.5,
) -> str:
    """Add an animation to a segment (intro, outro, or loop).

    Popular intro animations: 渐显 (fade in), 放大 (zoom in), 向上滑动 (slide up),
    动感放大 (dynamic zoom), Focus, Cubic_Flip, TV_On
    Popular outro animations: 渐隐 (fade out), 缩小 (zoom out), 向下滑动 (slide down)
    Popular loop animations: 左右摇摆, 翻转, 荡秋千

    Args:
        track_name: Track containing the segment
        segment_index: Index of the segment (0-based)
        animation_type: Animation name (e.g. "渐显", "放大", "Focus")
        category: "intro", "outro", or "loop"
        duration_s: Animation duration in seconds
    """
    result = dm.add_animation(track_name, segment_index, animation_type, category, duration_s)
    return json.dumps(result)


@server.tool()
async def add_transition(
    track_name: str,
    segment_index: int,
    transition_type: str,
    duration_s: float = 0.5,
) -> str:
    """Add a transition to a segment (plays between this and the previous segment).

    Popular transitions: 叠化 (dissolve), Flash, Flip_Zoom, Swirl, Cube_Rotate,
    Snap_Zoom, Bump, Film_Burn, White_Flash, Slide_Drop, Whirl

    Args:
        track_name: Track containing the segment
        segment_index: Index of the segment (must be > 0, transitions go between segments)
        transition_type: Transition name (e.g. "叠化", "Flash", "Flip_Zoom")
        duration_s: Transition duration in seconds
    """
    result = dm.add_transition(track_name, segment_index, transition_type, duration_s)
    return json.dumps(result)


@server.tool()
async def add_effect(
    track_name: str,
    segment_index: int,
    effect_type: str,
    category: str = "scene",
) -> str:
    """Add a video effect to a segment.

    Scene effects: 虚化 (blur), 噪点 (noise), 老电影 (old film), etc.
    Character effects: 美颜 (beauty), 磨皮 (skin smooth), 瘦脸 (slim face), etc.

    Args:
        track_name: Track containing the segment
        segment_index: Index of the segment
        effect_type: Effect name
        category: "scene" or "character"
    """
    result = dm.add_effect(track_name, segment_index, effect_type, category)
    return json.dumps(result)


@server.tool()
async def add_filter(
    track_name: str,
    segment_index: int,
    filter_type: str,
    intensity: int = 100,
) -> str:
    """Add a color filter/LUT to a segment.

    200+ filters available. Popular: 暖黄 (warm), 冷调 (cool), 复古 (retro),
    赛博朋克 (cyberpunk), 蒸汽波 (vaporwave), 日常 (daily), etc.

    Args:
        track_name: Track containing the segment
        segment_index: Index of the segment
        filter_type: Filter name
        intensity: Filter strength 0-100 (default 100)
    """
    result = dm.add_filter(track_name, segment_index, filter_type, intensity)
    return json.dumps(result)


@server.tool()
async def add_mask(
    track_name: str,
    segment_index: int,
    mask_type: str,
    size: float = 0.5,
    center_x: float = 0,
    center_y: float = 0,
    rotation: float = 0,
    feather: float = 0,
    invert: bool = False,
) -> str:
    """Add a mask to a segment.

    Mask types: 线性 (linear), 镜面 (mirror), 圆形 (circle),
    矩形 (rectangle), 爱心 (heart), 星形 (star)

    Args:
        track_name: Track containing the segment
        segment_index: Index of the segment
        mask_type: Mask shape name
        size: Mask size ratio 0-1
        center_x: Horizontal center position
        center_y: Vertical center position
        rotation: Rotation in degrees
        feather: Edge feathering 0-1
        invert: Invert the mask
    """
    result = dm.add_mask(track_name, segment_index, mask_type, size,
                         center_x, center_y, rotation, feather, invert)
    return json.dumps(result)


# ── Keyframes ────────────────────────────────────────────────────────

@server.tool()
async def add_keyframe(
    track_name: str,
    segment_index: int,
    property_name: str,
    time_offset_s: float,
    value: float,
) -> str:
    """Add a keyframe to animate a property over time on a segment.

    Properties: position_x, position_y, rotation, scale_x, scale_y,
    uniform_scale, alpha (opacity), saturation, contrast, brightness, volume

    Create smooth animations by setting keyframes at different times:
    - Ken Burns: uniform_scale 1.0 at 0s → 1.15 at 5s
    - Fade in: alpha 0.0 at 0s → 1.0 at 1s
    - Pan: position_x -0.2 at 0s → 0.2 at 5s

    Coordinates: position uses half-canvas units (center=0, edges=±1.0)
    Scale: 1.0 = original size

    Args:
        track_name: Track containing the segment
        segment_index: Index of the segment
        property_name: Property to animate (e.g. "uniform_scale", "position_x", "alpha")
        time_offset_s: Time offset from segment start in seconds
        value: Property value at this keyframe
    """
    result = dm.add_keyframe(track_name, segment_index, property_name, time_offset_s, value)
    return json.dumps(result)


# ── Pipeline / Batch ─────────────────────────────────────────────────

@server.tool()
async def build_reel(
    project_folder: str,
    preset_name: str = "slideshow",
    title_text: str = "",
    draft_name: str = "",
) -> str:
    """One-shot reel builder: project folder + preset → complete CapCut draft.

    Scans the project folder for images (reel_bg_*.png), creates a draft,
    sequences all images with the preset's transitions, animations, and
    keyframes, optionally adds a title, and saves to CapCut.

    Presets: "slideshow" (clean crossfades), "kenburns" (cinematic zoom+pan),
    "dynamic" (high-energy varied effects), "minimal" (simple fades)

    After this, just open CapCut Desktop and the reel is ready to export.

    Args:
        project_folder: Path to the UGAFRICA project folder (contains images/ subfolder)
        preset_name: Preset style — "slideshow", "kenburns", "dynamic", or "minimal"
        title_text: Optional title text overlay (empty = auto-generate or none)
        draft_name: Optional custom draft name (empty = auto from folder name)
    """
    result = dm.build_reel(project_folder, preset_name,
                           title_text or None, draft_name or None)
    return json.dumps(result)


@server.tool()
async def add_track(
    track_type: str,
    name: str = "",
    mute: bool = False,
) -> str:
    """Add a named track for multi-layer compositions.

    Track types: video, audio, text, effect, filter, sticker
    Use multiple video tracks for overlays, multiple audio tracks
    for music + voiceover, etc.

    Args:
        track_type: One of: video, audio, text, effect, filter, sticker
        name: Track name (auto-generated if empty)
        mute: Mute this track
    """
    result = dm.add_track(track_type, name or None, mute)
    return json.dumps(result)


@server.tool()
async def list_presets() -> str:
    """List available reel presets with descriptions.

    Use these preset names with the build_reel tool.
    """
    return json.dumps(list_all_presets())


# ── MCP Resources ────────────────────────────────────────────────────

@server.resource("capcut://projects")
async def projects_resource() -> str:
    """List all UGAFRICA project folders with their image counts."""
    return json.dumps(dm.list_projects())


@server.resource("capcut://draft-info")
async def draft_info_resource() -> str:
    """Get the current active draft state."""
    try:
        return json.dumps(dm.get_draft_info())
    except RuntimeError:
        return json.dumps({"status": "no_active_draft"})


# ── MCP Prompts ──────────────────────────────────────────────────────

@server.prompt()
async def create_reel(project_name: str = "", style: str = "") -> str:
    """Guided reel creation prompt."""
    projects = dm.list_projects()
    project_list = "\n".join(f"- {p['name']} ({p['image_count']} images)" for p in projects)
    presets = "\n".join(f"- {p['name']}: {p['description']}" for p in list_all_presets())

    return f"""Create a UGAFRICA reel. Here are the available projects and presets:

**Projects:**
{project_list or "No projects found in the projects directory."}

**Presets:**
{presets}

{"Selected project: " + project_name if project_name else "Which project should I use?"}
{"Selected style: " + style if style else "Which preset style do you want?"}

Once confirmed, I'll use build_reel to create the draft, then you can open CapCut to preview and export."""


@server.prompt()
async def edit_draft() -> str:
    """Context-aware draft editing prompt."""
    try:
        info = dm.get_draft_info()
        tracks = "\n".join(f"  - {t['name']} ({t['type']}): {t['segments']} segments" for t in info["tracks"])
        return f"""Active draft: **{info['name']}**
- Dimensions: {info['width']}x{info['height']} @ {info['fps']}fps
- Duration: {info['duration_s']:.1f}s
- Tracks:
{tracks}

What would you like to change? I can:
- Add/remove media, text, or audio
- Apply animations, transitions, effects, or filters
- Add keyframe animations (Ken Burns, zoom, pan, fade)
- Add masks or adjust segment properties
- Import subtitles from an .srt file"""
    except RuntimeError:
        return "No active draft. Use create_draft or open_draft to start, or build_reel for a one-shot pipeline."


@server.prompt()
async def batch_reels() -> str:
    """Batch reel creation prompt."""
    projects = dm.list_projects()
    project_list = "\n".join(f"- {p['name']} ({p['image_count']} images)" for p in projects)
    presets = "\n".join(f"- {p['name']}: {p['description']}" for p in list_all_presets())

    return f"""Batch reel creation. I'll create drafts for multiple projects.

**Available projects:**
{project_list or "No projects found."}

**Presets:**
{presets}

Which projects do you want to process, and which preset for each?
I'll run build_reel for each one."""


# ── Load Plugins & Run ───────────────────────────────────────────────

loaded_plugins = load_plugins(server, dm)
if loaded_plugins:
    print(f"[capcut-mcp] Loaded plugins: {', '.join(loaded_plugins)}", file=sys.stderr)

if __name__ == "__main__":
    server.run(transport="stdio")
