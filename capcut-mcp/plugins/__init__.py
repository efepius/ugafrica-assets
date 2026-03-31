"""Plugin auto-discovery for capcut-mcp.

Drop a .py file in this directory with a `register(server, draft_manager)` function
and it will be auto-loaded when the MCP server starts.

Example plugin (plugins/photoshop.py):

    def register(server, draft_manager):
        @server.tool()
        async def ps_create_overlay(text: str, style: str, output_path: str) -> str:
            \"\"\"Create a styled text overlay in Photoshop, export as PNG.\"\"\"
            # Your Photoshop automation here
            return json.dumps({"status": "created", "path": output_path})

Future plugins:
- photoshop.py  — Title cards, lower thirds, image compositing via Photoshop
- flstudio.py   — Export stems, beat detection, auto-sync audio to timeline
- dalle.py      — Generate images from prompts, save to project folder
- social.py     — Auto-format for Instagram/TikTok/YouTube Shorts
"""

import os
import importlib
import sys


def load_plugins(server, draft_manager):
    """Scan this directory for plugin modules and call their register() function."""
    plugin_dir = os.path.dirname(__file__)
    loaded = []

    for filename in sorted(os.listdir(plugin_dir)):
        if filename.startswith("_") or not filename.endswith(".py"):
            continue
        module_name = filename[:-3]
        module_path = os.path.join(plugin_dir, filename)

        try:
            spec = importlib.util.spec_from_file_location(f"plugins.{module_name}", module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            if hasattr(module, "register"):
                module.register(server, draft_manager)
                loaded.append(module_name)
        except Exception as e:
            print(f"[capcut-mcp] Warning: Failed to load plugin '{module_name}': {e}", file=sys.stderr)

    return loaded
