# Character Animation Creator Skill

## Showcase

Watch the skill in action — generating a complete 128×128 character spritesheet from a single prompt:  
**[View on X (Twitter)](https://x.com/smolekoma/status/2051075092847919276?s=20)**

---

**For:** Codex (OpenAI) and GPT Web Agent  
**Purpose:** Generate game-ready 128×128 anime-style character spritesheets with 8-direction animations from a text prompt or reference image.

## What It Does

```text
"Use game-character-128 to make a 128x128 knight with 8-direction walk and attack
animations from this image."
```

Given a concept or reference image, this skill:

1. **Establishes character identity** — species, class, silhouette, palette, weapon, outfit.
2. **Generates a canonical base sprite** — a readable high-density 128×128 anime game sprite.
3. **Produces animation strips** — idle, walk, attack for all 8 directions (24 rows × 6 columns).
4. **Runs pixel cleanup** — quantizes palettes, snaps edges, handles alpha.
5. **Validates the atlas** — checks frame integrity and generates a contact sheet.
6. **Packages output** — final spritesheet + QA report ready for import into RPGs, roguelikes, top-down action games, or tactics engines.

## Default Output Layout

```
run/
├── prompts/
├── generated/              # raw strips from image generation
├── final/
│   ├── character-sheet.png
│   └── character-sheet-clean.png
└── qa/
    ├── validation.json
    └── contact-sheet.png
```

## Direction Set

Default 8-direction order:

```text
south, south-east, east, north-east, north, north-west, west, south-west
```

## Animation Rows

| Action  | Frames | Notes                        |
|---------|--------|------------------------------|
| idle    | 4      | padded to 6 cells            |
| walk    | 6      | full cycle                   |
| attack  | 6      | full cycle                   |

**Default atlas:** `768 × 3072` (6 columns × 24 rows × 128px).

Smaller scopes available:
- `walk-only`: 8 rows × 6 frames, `768 × 1024`
- `idle-walk`: 16 rows × 6 frames, `768 × 2048`
- `walk-attack`: 16 rows × 6 frames, `768 × 2048`
- `combat`: idle + walk + attack for all 8 directions, `768 × 3072`

## Quick Use Example

```text
"Use game-character-128 to make a 128x128 knight with 8-direction walk and attack
animations from this image."
```

## Scripts

- `scripts/pixel_snap.py` — alpha threshold, palette quantization, pixelate-scale edge hardening
- `scripts/alpha_from_bw_pair.py` — create transparent PNG alpha from matching black/white background renders
- `scripts/export_png_loop_preview.py` — static HTML previews that loop PNG atlas frames without GIF dithering
- `scripts/validate_character_sheet.py` — frame validation + contact-sheet generation
- `scripts/export_animation_previews.py` — export GIF/PNG previews per animation row

## Requirements

- Python 3.9+
- Pillow (`pip install Pillow`)
- Image generation backend (Codex/GPT `$imagegen` or DALL-E / Midjourney / etc.)

## License

MIT — see [SKILL.md](SKILL.md) for full workflow documentation.
