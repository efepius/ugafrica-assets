# UGAFRICA Assets

## Project Overview
This repo stores DALL-E generated images for UGAFRICA reels and includes an MCP server for CapCut Desktop video editing automation.

## Reel Production Pipeline
1. Generate DALL-E images → stored in `projects/<artist>-<topic>-<date>-<hash>/images/`
2. Use CapCut MCP tools to create a draft from the images
3. Open CapCut Desktop to preview, tweak, and export

## Project Structure
- `projects/` — DALL-E generated reel images
  - Each subfolder: `<artist>-<topic>-<date>-<hash>/images/reel_bg_XX.png`
- `capcut-mcp/` — MCP server for CapCut Desktop editing

## CapCut MCP Server (`capcut-mcp/`)

### Quick Reel (one command)
Use `build_reel` with a project folder path and preset name:
- **slideshow** — Clean crossfades + subtle zoom (professional)
- **kenburns** — Alternating zoom/pan (cinematic)
- **dynamic** — Varied animations + transitions (social media energy)
- **minimal** — Simple fades (elegant)

### Step-by-Step Editing
1. `create_draft` — New project (default 1080x1920 @30fps vertical reel)
2. `add_image` / `add_video` / `add_audio` — Add media to timeline
3. `add_text` — Text overlays with full styling
4. `add_transition` — Between segments (叠化=dissolve, Flash, Flip_Zoom, etc.)
5. `add_animation` — Intro/outro effects (渐显=fade in, 放大=zoom in, etc.)
6. `add_keyframe` — Smooth motion (Ken Burns, zoom, pan, fade)
7. `add_filter` / `add_effect` / `add_mask` — Color grading and effects
8. `save_draft` — Save to CapCut's drafts folder

### Defaults for UGAFRICA Reels
- Resolution: 1080x1920 (vertical/portrait)
- FPS: 30
- Image duration: 3-5 seconds per image
- Always add transitions between images
- Title text: bold white with black border, positioned near bottom (position_y=-0.6)

### Time & Coordinate System
- Time: seconds in tool parameters (internally microseconds)
- Position: -1.0 to 1.0 (center = 0, edges = ±1.0)
- Scale: 1.0 = original size

### Audio Notes
- FL Studio exports (WAV/MP3) can be added directly with `add_audio`
- Use `fade_in_s` and `fade_out_s` for smooth audio transitions
- Multiple audio tracks supported (music + voiceover)

## Plugin System
`capcut-mcp/plugins/` — Drop-in extensibility. Future: Photoshop, FL Studio, DALL-E integrations.
