"""Stateful draft manager wrapping pycapcut for MCP tool operations."""

import os
import glob
import json
import random
from pathlib import Path
from typing import Optional

import pycapcut as cc
from pycapcut import (
    ScriptFile, DraftFolder, VideoMaterial, AudioMaterial,
    VideoSegment, AudioSegment, TextSegment, TextStyle,
    ClipSettings, Timerange, TrackType, KeyframeProperty,
    SEC,
)
from pycapcut.time_util import tim
from pycapcut.text_segment import TextBorder, TextBackground
from pycapcut.metadata import (
    IntroType, OutroType, GroupAnimationType,
    TransitionType, FilterType,
    VideoSceneEffectType, VideoCharacterEffectType,
)
from pycapcut.video_segment import MaskType

from presets import get_preset, list_all_presets, PRESETS


DEFAULT_WIDTH = 1080
DEFAULT_HEIGHT = 1920
DEFAULT_FPS = 30


class DraftManager:
    """Manages a single active CapCut draft with stateful operations."""

    def __init__(self, drafts_path: Optional[str] = None, projects_path: Optional[str] = None):
        self.drafts_path = drafts_path or os.environ.get(
            "CAPCUT_DRAFTS_PATH",
            os.path.expanduser("~/AppData/Local/CapCut/User Data/Projects/com.lveditor.draft")
        )
        self.projects_path = projects_path or os.environ.get(
            "UGAFRICA_PROJECTS_PATH",
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "projects")
        )
        self.script: Optional[ScriptFile] = None
        self.draft_folder: Optional[DraftFolder] = None
        self.draft_name: Optional[str] = None
        self._track_counter = {"video": 0, "audio": 0, "text": 0, "effect": 0, "filter": 0, "sticker": 0}
        self._segment_index = {"video": 0, "audio": 0, "text": 0}

    def _require_draft(self):
        if self.script is None:
            raise RuntimeError("No active draft. Call create_draft or open_draft first.")

    def _get_draft_folder(self) -> DraftFolder:
        if self.draft_folder is None:
            self.draft_folder = DraftFolder(self.drafts_path)
        return self.draft_folder

    # ── Draft Lifecycle ──────────────────────────────────────────────

    def create_draft(self, name: str, width: int = DEFAULT_WIDTH,
                     height: int = DEFAULT_HEIGHT, fps: int = DEFAULT_FPS) -> dict:
        folder = self._get_draft_folder()
        self.script = folder.create_draft(name, width, height, fps, allow_replace=True)
        self.draft_name = name
        self._track_counter = {"video": 0, "audio": 0, "text": 0, "effect": 0, "filter": 0, "sticker": 0}
        self._segment_index = {"video": 0, "audio": 0, "text": 0}
        return {"name": name, "width": width, "height": height, "fps": fps, "status": "created"}

    def open_draft(self, name: str) -> dict:
        folder = self._get_draft_folder()
        self.script = folder.load_template(name)
        self.draft_name = name
        return {"name": name, "width": self.script.width, "height": self.script.height,
                "fps": self.script.fps, "duration_s": self.script.duration / SEC, "status": "opened"}

    def duplicate_draft(self, source_name: str, new_name: str) -> dict:
        folder = self._get_draft_folder()
        self.script = folder.duplicate_as_template(source_name, new_name, allow_replace=True)
        self.draft_name = new_name
        return {"source": source_name, "new_name": new_name, "status": "duplicated"}

    def save_draft(self) -> dict:
        self._require_draft()
        self.script.save()
        return {"name": self.draft_name, "duration_s": self.script.duration / SEC,
                "path": self.drafts_path, "status": "saved"}

    def list_drafts(self) -> list:
        folder = self._get_draft_folder()
        names = folder.list_drafts()
        results = []
        for name in names:
            results.append({"name": name})
        return results

    def get_draft_info(self) -> dict:
        self._require_draft()
        tracks = []
        for name, track in self.script.tracks.items():
            tracks.append({
                "name": name,
                "type": track.track_type.name,
                "segments": len(track.segments),
            })
        return {
            "name": self.draft_name,
            "width": self.script.width,
            "height": self.script.height,
            "fps": self.script.fps,
            "duration_s": self.script.duration / SEC,
            "tracks": tracks,
        }

    # ── Track Management ─────────────────────────────────────────────

    def add_track(self, track_type: str, name: Optional[str] = None, mute: bool = False) -> dict:
        self._require_draft()
        tt = TrackType[track_type]
        if name is None:
            self._track_counter[track_type] = self._track_counter.get(track_type, 0) + 1
            count = self._track_counter[track_type]
            name = f"{track_type}_{count}" if count > 1 else track_type
        try:
            self.script.add_track(tt, name, mute=mute)
        except NameError:
            pass  # Track already exists with this name
        return {"track": name, "type": track_type}

    def _ensure_track(self, track_type: str, track_name: Optional[str] = None) -> str:
        """Ensure a track exists and return its name."""
        tt = TrackType[track_type]
        existing = [t for t in self.script.tracks.values() if t.track_type == tt]
        if track_name and track_name in self.script.tracks:
            return track_name
        if not track_name and existing:
            return existing[0].name
        name = track_name or track_type
        try:
            self.script.add_track(tt, name)
        except NameError:
            pass
        return name

    # ── Media ────────────────────────────────────────────────────────

    def add_video(self, path: str, start_s: float = 0, duration_s: float = 5,
                  speed: float = 1.0, volume: float = 1.0,
                  scale: float = 1.0, position_x: float = 0, position_y: float = 0,
                  rotation: float = 0, opacity: float = 1.0,
                  track_name: Optional[str] = None) -> dict:
        self._require_draft()
        track_name = self._ensure_track("video", track_name)
        material = VideoMaterial(path)
        self.script.add_material(material)
        clip = ClipSettings(
            scale_x=scale, scale_y=scale,
            transform_x=position_x, transform_y=position_y,
            rotation=rotation, alpha=opacity,
        )
        start = int(start_s * SEC)
        dur = int(duration_s * SEC)
        seg = VideoSegment(material, Timerange(start, dur), clip_settings=clip,
                           speed=speed, volume=volume)
        self.script.add_segment(seg, track_name)
        self._segment_index["video"] += 1
        return {"type": "video", "path": path, "start_s": start_s, "duration_s": duration_s,
                "track": track_name, "segment_index": self._segment_index["video"] - 1}

    def add_image(self, path: str, start_s: float = 0, duration_s: float = 4,
                  scale: float = 1.0, position_x: float = 0, position_y: float = 0,
                  rotation: float = 0, opacity: float = 1.0,
                  track_name: Optional[str] = None) -> dict:
        self._require_draft()
        track_name = self._ensure_track("video", track_name)
        material = VideoMaterial(path)
        self.script.add_material(material)
        clip = ClipSettings(
            scale_x=scale, scale_y=scale,
            transform_x=position_x, transform_y=position_y,
            rotation=rotation, alpha=opacity,
        )
        start = int(start_s * SEC)
        dur = int(duration_s * SEC)
        seg = VideoSegment(material, Timerange(start, dur), clip_settings=clip)
        self.script.add_segment(seg, track_name)
        self._segment_index["video"] += 1
        return {"type": "image", "path": path, "start_s": start_s, "duration_s": duration_s,
                "track": track_name, "segment_index": self._segment_index["video"] - 1}

    def add_audio(self, path: str, start_s: float = 0, duration_s: Optional[float] = None,
                  volume: float = 1.0, fade_in_s: float = 0, fade_out_s: float = 0,
                  track_name: Optional[str] = None) -> dict:
        self._require_draft()
        track_name = self._ensure_track("audio", track_name)
        material = AudioMaterial(path)
        self.script.add_material(material)
        start = int(start_s * SEC)
        dur = int((duration_s if duration_s else material.duration / SEC) * SEC)
        seg = AudioSegment(material, Timerange(start, dur), volume=volume)
        if fade_in_s > 0 or fade_out_s > 0:
            seg.add_fade(
                in_duration=int(fade_in_s * SEC),
                out_duration=int(fade_out_s * SEC),
            )
        self.script.add_segment(seg, track_name)
        self._segment_index["audio"] += 1
        return {"type": "audio", "path": path, "start_s": start_s, "duration_s": dur / SEC,
                "track": track_name}

    # ── Text ─────────────────────────────────────────────────────────

    def add_text(self, content: str, start_s: float = 0, duration_s: float = 3,
                 font_size: float = 8.0, color: list = None, bold: bool = False,
                 italic: bool = False, align: int = 1,
                 border_color: list = None, border_width: float = 0,
                 bg_color: str = "", bg_alpha: float = 0.7,
                 position_x: float = 0, position_y: float = 0,
                 scale: float = 1.0, rotation: float = 0,
                 track_name: Optional[str] = None) -> dict:
        self._require_draft()
        track_name = self._ensure_track("text", track_name)
        color = color or [1.0, 1.0, 1.0]
        style = TextStyle(
            size=font_size, bold=bold, italic=italic,
            color=tuple(color), align=align,
        )
        border = None
        if border_width > 0:
            border_color = border_color or [0.0, 0.0, 0.0]
            border = TextBorder(color=tuple(border_color), width=border_width)
        background = None
        if bg_color:
            background = TextBackground(color=bg_color, alpha=bg_alpha)
        clip = ClipSettings(
            transform_x=position_x, transform_y=position_y,
            scale_x=scale, scale_y=scale, rotation=rotation,
        )
        start = int(start_s * SEC)
        dur = int(duration_s * SEC)
        seg = TextSegment(content, Timerange(start, dur), style=style,
                          border=border, background=background, clip_settings=clip)
        self.script.add_segment(seg, track_name)
        self._segment_index["text"] += 1
        return {"type": "text", "content": content, "start_s": start_s,
                "duration_s": duration_s, "track": track_name}

    def import_subtitles(self, srt_path: str, track_name: Optional[str] = None,
                         font_size: float = 6.0, color: list = None,
                         bold: bool = True) -> dict:
        self._require_draft()
        track_name = self._ensure_track("text", track_name)
        color = color or [1.0, 1.0, 1.0]
        style = TextStyle(size=font_size, bold=bold, color=tuple(color), align=1)
        border = TextBorder(color=(0.0, 0.0, 0.0), width=50.0)
        self.script.import_srt(srt_path, track_name, style=style, border=border)
        return {"type": "subtitles", "path": srt_path, "track": track_name}

    # ── Effects & Style ──────────────────────────────────────────────

    def add_animation(self, track_name: str, segment_index: int,
                      animation_type: str, category: str = "intro",
                      duration_s: float = 0.5) -> dict:
        self._require_draft()
        track = self.script.tracks.get(track_name)
        if not track:
            raise RuntimeError(f"Track '{track_name}' not found.")
        seg = track.segments[segment_index]
        dur = int(duration_s * SEC)
        if category == "intro":
            anim = getattr(IntroType, animation_type)
        elif category == "outro":
            anim = getattr(OutroType, animation_type)
        elif category == "loop":
            anim = getattr(GroupAnimationType, animation_type)
        else:
            raise ValueError(f"Unknown animation category '{category}'. Use intro, outro, or loop.")
        seg.add_animation(anim, duration=dur)
        return {"animation": animation_type, "category": category, "duration_s": duration_s,
                "track": track_name, "segment": segment_index}

    def add_transition(self, track_name: str, segment_index: int,
                       transition_type: str, duration_s: float = 0.5) -> dict:
        self._require_draft()
        track = self.script.tracks.get(track_name)
        if not track:
            raise RuntimeError(f"Track '{track_name}' not found.")
        seg = track.segments[segment_index]
        trans = getattr(TransitionType, transition_type)
        seg.add_transition(trans, duration=int(duration_s * SEC))
        return {"transition": transition_type, "duration_s": duration_s,
                "track": track_name, "segment": segment_index}

    def add_effect(self, track_name: str, segment_index: int,
                   effect_type: str, category: str = "scene") -> dict:
        self._require_draft()
        track = self.script.tracks.get(track_name)
        if not track:
            raise RuntimeError(f"Track '{track_name}' not found.")
        seg = track.segments[segment_index]
        if category == "scene":
            effect = getattr(VideoSceneEffectType, effect_type)
        elif category == "character":
            effect = getattr(VideoCharacterEffectType, effect_type)
        else:
            raise ValueError(f"Unknown effect category '{category}'. Use scene or character.")
        seg.add_effect(effect)
        return {"effect": effect_type, "category": category,
                "track": track_name, "segment": segment_index}

    def add_filter(self, track_name: str, segment_index: int,
                   filter_type: str, intensity: int = 100) -> dict:
        self._require_draft()
        track = self.script.tracks.get(track_name)
        if not track:
            raise RuntimeError(f"Track '{track_name}' not found.")
        seg = track.segments[segment_index]
        filt = getattr(FilterType, filter_type)
        seg.add_filter(filt, intensity=intensity)
        return {"filter": filter_type, "intensity": intensity,
                "track": track_name, "segment": segment_index}

    def add_mask(self, track_name: str, segment_index: int,
                 mask_type: str, size: float = 0.5,
                 center_x: float = 0, center_y: float = 0,
                 rotation: float = 0, feather: float = 0,
                 invert: bool = False) -> dict:
        self._require_draft()
        track = self.script.tracks.get(track_name)
        if not track:
            raise RuntimeError(f"Track '{track_name}' not found.")
        seg = track.segments[segment_index]
        mask = getattr(MaskType, mask_type)
        seg.add_mask(mask, center_x=center_x, center_y=center_y,
                     size=size, rotation=rotation, feather=feather, invert=invert)
        return {"mask": mask_type, "size": size, "track": track_name, "segment": segment_index}

    # ── Keyframes ────────────────────────────────────────────────────

    def add_keyframe(self, track_name: str, segment_index: int,
                     property_name: str, time_offset_s: float, value: float) -> dict:
        self._require_draft()
        track = self.script.tracks.get(track_name)
        if not track:
            raise RuntimeError(f"Track '{track_name}' not found.")
        seg = track.segments[segment_index]
        prop = getattr(KeyframeProperty, property_name)
        offset = int(time_offset_s * SEC)
        seg.add_keyframe(prop, offset, value)
        return {"property": property_name, "time_s": time_offset_s, "value": value,
                "track": track_name, "segment": segment_index}

    # ── Pipeline / Batch ─────────────────────────────────────────────

    def build_reel(self, project_folder: str, preset_name: str = "slideshow",
                   title_text: Optional[str] = None, draft_name: Optional[str] = None) -> dict:
        """One-shot: scan project images → create draft → sequence with preset → save."""
        preset = get_preset(preset_name)

        # Find images
        img_dir = os.path.join(project_folder, "images")
        if not os.path.isdir(img_dir):
            img_dir = project_folder
        patterns = ["reel_bg_*.png", "reel_bg_*.jpg", "*.png", "*.jpg"]
        images = []
        for pat in patterns:
            images = sorted(glob.glob(os.path.join(img_dir, pat)))
            if images:
                break
        if not images:
            raise RuntimeError(f"No images found in {img_dir}")

        # Create draft
        if not draft_name:
            draft_name = os.path.basename(project_folder.rstrip("/\\")) + "_reel"
        self.create_draft(draft_name)
        self._ensure_track("video", "main")

        img_dur = preset["image_duration_s"]
        segments_added = []

        for i, img_path in enumerate(images):
            start_s = i * img_dur

            result = self.add_image(img_path, start_s=start_s, duration_s=img_dur, track_name="main")
            seg_idx = result["segment_index"]
            segments_added.append(result)

            # Apply keyframes
            kf = preset.get("keyframes")
            if kf:
                if kf["pattern"] == "zoom_in":
                    self.add_keyframe("main", seg_idx, "uniform_scale", 0, kf["start_scale"])
                    self.add_keyframe("main", seg_idx, "uniform_scale", img_dur, kf["end_scale"])
                elif kf["pattern"] == "alternating":
                    p = kf["patterns"][i % len(kf["patterns"])]
                    self.add_keyframe("main", seg_idx, "uniform_scale", 0, p["start_scale"])
                    self.add_keyframe("main", seg_idx, "uniform_scale", img_dur, p["end_scale"])
                    if "start_x" in p:
                        self.add_keyframe("main", seg_idx, "position_x", 0, p["start_x"])
                        self.add_keyframe("main", seg_idx, "position_x", img_dur, p["end_x"])
                    if "start_y" in p:
                        self.add_keyframe("main", seg_idx, "position_y", 0, p["start_y"])
                        self.add_keyframe("main", seg_idx, "position_y", img_dur, p["end_y"])

            # Apply intro animation
            intro = preset.get("intro")
            if intro and isinstance(intro, dict):
                if intro.get("type") == "varied":
                    anim_name = random.choice(intro["options"])
                else:
                    anim_name = intro["type"]
                try:
                    self.add_animation("main", seg_idx, anim_name, "intro", intro.get("duration_s", 0.5))
                except Exception:
                    pass  # Skip if animation not compatible

            # Apply outro animation
            outro = preset.get("outro")
            if outro and isinstance(outro, dict):
                if outro.get("type") == "varied":
                    anim_name = random.choice(outro["options"])
                else:
                    anim_name = outro["type"]
                try:
                    self.add_animation("main", seg_idx, anim_name, "outro", outro.get("duration_s", 0.5))
                except Exception:
                    pass

            # Apply transition (on segments after the first)
            trans = preset.get("transition")
            if trans and i > 0:
                if trans.get("type") == "varied":
                    trans_name = random.choice(trans["options"])
                else:
                    trans_name = trans["type"]
                try:
                    self.add_transition("main", seg_idx, trans_name, trans.get("duration_s", 0.5))
                except Exception:
                    pass

        # Add title text if requested
        title_conf = preset.get("title") or {}
        if title_text or title_conf.get("enabled"):
            text = title_text or draft_name.replace("_", " ").replace("-", " ").title()
            self._ensure_track("text", "titles")
            style_conf = title_conf.get("style", {})
            self.add_text(
                text, start_s=0, duration_s=img_dur,
                font_size=style_conf.get("size", 10.0),
                bold=style_conf.get("bold", True),
                color=style_conf.get("color", [1.0, 1.0, 1.0]),
                align=style_conf.get("align", 1),
                border_color=style_conf.get("border_color", [0.0, 0.0, 0.0]),
                border_width=style_conf.get("border_width", 50.0),
                position_y=-0.6,
                track_name="titles",
            )

        # Save
        self.save_draft()

        return {
            "draft_name": draft_name,
            "preset": preset_name,
            "images": len(images),
            "duration_s": self.script.duration / SEC,
            "title": title_text,
            "status": "saved",
            "path": self.drafts_path,
        }

    def import_project_images(self, project_folder: str, duration_per_image_s: float = 4.0,
                              track_name: Optional[str] = None) -> dict:
        """Bulk import all images from a UGAFRICA project folder onto the timeline."""
        self._require_draft()
        track_name = self._ensure_track("video", track_name)

        img_dir = os.path.join(project_folder, "images")
        if not os.path.isdir(img_dir):
            img_dir = project_folder

        patterns = ["reel_bg_*.png", "reel_bg_*.jpg", "*.png", "*.jpg"]
        images = []
        for pat in patterns:
            images = sorted(glob.glob(os.path.join(img_dir, pat)))
            if images:
                break
        if not images:
            raise RuntimeError(f"No images found in {img_dir}")

        results = []
        for i, img_path in enumerate(images):
            start_s = i * duration_per_image_s
            result = self.add_image(img_path, start_s=start_s,
                                    duration_s=duration_per_image_s, track_name=track_name)
            results.append(result)

        return {"images_added": len(results), "track": track_name,
                "total_duration_s": len(results) * duration_per_image_s}

    # ── Resource helpers ─────────────────────────────────────────────

    def list_projects(self) -> list:
        """List UGAFRICA project folders with image counts."""
        results = []
        if not os.path.isdir(self.projects_path):
            return results
        for entry in sorted(os.listdir(self.projects_path)):
            proj_dir = os.path.join(self.projects_path, entry)
            if not os.path.isdir(proj_dir):
                continue
            img_dir = os.path.join(proj_dir, "images")
            if os.path.isdir(img_dir):
                imgs = [f for f in os.listdir(img_dir) if f.endswith((".png", ".jpg"))]
            else:
                imgs = [f for f in os.listdir(proj_dir) if f.endswith((".png", ".jpg"))]
            results.append({"name": entry, "path": proj_dir, "image_count": len(imgs)})
        return results
