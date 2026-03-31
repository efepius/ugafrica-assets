# CapCut Desktop MCP Server

MCP server that gives Claude full control over CapCut Desktop video editing. Built for the UGAFRICA reel production pipeline.

## What it does

- Creates and edits CapCut projects programmatically via `draft_content.json`
- 20 tools: draft management, media, text, effects, filters, animations, transitions, masks, keyframes
- 4 reel presets: slideshow, kenburns, dynamic, minimal
- One-shot `build_reel` tool: project folder → complete CapCut draft in seconds
- Plugin system for future Photoshop, FL Studio, and DALL-E integrations

## Setup

### 1. Install dependencies

```bash
pip install mcp pycapcut
```

### 2. Find your CapCut drafts path

On Windows (default):
```
C:\Users\<YOU>\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft
```

### 3. Add to Claude Desktop config

Edit `%APPDATA%\Claude\claude_desktop_config.json` (Windows) or `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac):

```json
{
  "mcpServers": {
    "capcut": {
      "command": "python3",
      "args": ["server.py"],
      "cwd": "C:\\path\\to\\ugafrica-assets\\capcut-mcp",
      "env": {
        "CAPCUT_DRAFTS_PATH": "C:\\Users\\YOU\\AppData\\Local\\CapCut\\User Data\\Projects\\com.lveditor.draft"
      }
    }
  }
}
```

### 4. Add to Claude Code config

```bash
claude mcp add capcut -- python3 /path/to/ugafrica-assets/capcut-mcp/server.py
```

Or edit `.claude/settings.json`:
```json
{
  "mcpServers": {
    "capcut": {
      "command": "python3",
      "args": ["/path/to/ugafrica-assets/capcut-mcp/server.py"],
      "env": {
        "CAPCUT_DRAFTS_PATH": "C:\\Users\\YOU\\AppData\\Local\\CapCut\\User Data\\Projects\\com.lveditor.draft"
      }
    }
  }
}
```

## Usage

### Quick: One-shot reel

> "Create a kenburns reel from the Burna Boy project with title 'Who Is Burna Boy?'"

Claude calls `build_reel` → images sequenced with Ken Burns zoom/pan + dissolve transitions + title → saved to CapCut. Open CapCut and export.

### Custom: Step by step

> "Create a new 1080x1920 draft called 'my-reel', add the 4 Burna Boy images at 3 seconds each, add a dissolve transition between each, put a title at the bottom, and add my FL Studio beat as background music"

Claude chains: `create_draft` → `add_image` x4 → `add_transition` x3 → `add_text` → `add_audio` → `save_draft`

## Tools (20)

| Category | Tools |
|----------|-------|
| Draft | `create_draft`, `open_draft`, `save_draft`, `list_drafts`, `get_draft_info`, `duplicate_draft` |
| Media | `add_video`, `add_image`, `add_audio` |
| Text | `add_text`, `import_subtitles` |
| Effects | `add_animation`, `add_transition`, `add_effect`, `add_filter`, `add_mask` |
| Motion | `add_keyframe` |
| Pipeline | `build_reel`, `add_track`, `list_presets` |

## Plugins

Drop a `.py` file in `plugins/` with a `register(server, draft_manager)` function. It auto-loads on startup.

Planned plugins:
- `photoshop.py` — Title cards, compositing, image processing
- `flstudio.py` — Audio stems, beat sync, auto-timing
- `dalle.py` — Image generation from prompts
- `social.py` — Auto-format for IG/TikTok/YouTube Shorts
