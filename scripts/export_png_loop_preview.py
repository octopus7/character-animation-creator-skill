#!/usr/bin/env python3
"""Write a static HTML preview that loops frames directly from a PNG atlas."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    :root {{
      color-scheme: dark;
      font-family: Arial, sans-serif;
      background: #151820;
      color: #e7eaf0;
    }}
    body {{
      margin: 0;
      padding: 24px;
    }}
    .toolbar {{
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 18px;
      flex-wrap: wrap;
    }}
    h1 {{
      font-size: 18px;
      font-weight: 600;
      margin: 0 16px 0 0;
    }}
    label {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 13px;
      color: #bdc4d4;
    }}
    input[type="range"] {{
      width: 160px;
    }}
    button {{
      height: 30px;
      border: 1px solid #3b4252;
      background: #232936;
      color: #eef2f8;
      border-radius: 6px;
      padding: 0 12px;
      cursor: pointer;
    }}
    .stage {{
      display: grid;
      gap: 14px;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      align-items: start;
    }}
    .preview {{
      display: grid;
      gap: 8px;
      justify-items: start;
    }}
    .name {{
      font-size: 13px;
      color: #c8ceda;
    }}
    canvas {{
      border: 1px solid #2f3748;
      background-color: #2a2f3b;
      background-image:
        linear-gradient(45deg, #3f4656 25%, transparent 25%),
        linear-gradient(-45deg, #3f4656 25%, transparent 25%),
        linear-gradient(45deg, transparent 75%, #3f4656 75%),
        linear-gradient(-45deg, transparent 75%, #3f4656 75%);
      background-size: 16px 16px;
      background-position: 0 0, 0 8px, 8px -8px, -8px 0;
      image-rendering: auto;
    }}
  </style>
</head>
<body>
  <div class="toolbar">
    <h1>{title}</h1>
    <button id="toggle" type="button">Pause</button>
    <label>FPS <input id="fps" type="range" min="3" max="18" value="{fps}"> <span id="fpsValue">{fps}</span></label>
    <label>Scale <input id="scale" type="range" min="1" max="4" value="{scale}"> <span id="scaleValue">{scale}x</span></label>
  </div>
  <div id="stage" class="stage"></div>

  <script>
    const atlasUrl = {atlas_url};
    const cell = {cell};
    const columns = {columns};
    const rows = {rows};

    const image = new Image();
    const stage = document.getElementById('stage');
    const fpsInput = document.getElementById('fps');
    const fpsValue = document.getElementById('fpsValue');
    const scaleInput = document.getElementById('scale');
    const scaleValue = document.getElementById('scaleValue');
    const toggle = document.getElementById('toggle');
    let paused = false;
    let frame = 0;
    let lastTick = 0;
    const canvases = [];

    function checker(ctx, width, height, block) {{
      ctx.fillStyle = '#2a2f3b';
      ctx.fillRect(0, 0, width, height);
      ctx.fillStyle = '#3f4656';
      for (let y = 0; y < height; y += block) {{
        for (let x = 0; x < width; x += block) {{
          if (((x / block) + (y / block)) % 2 === 0) {{
            ctx.fillRect(x, y, block, block);
          }}
        }}
      }}
    }}

    function drawAll() {{
      const scale = Number(scaleInput.value);
      for (const item of canvases) {{
        const size = cell * scale;
        item.canvas.width = size;
        item.canvas.height = size;
        item.canvas.style.width = `${{size}}px`;
        item.canvas.style.height = `${{size}}px`;
        const ctx = item.canvas.getContext('2d');
        ctx.imageSmoothingEnabled = true;
        checker(ctx, size, size, 8 * scale);
        ctx.drawImage(image, frame * cell, item.row * cell, cell, cell, 0, 0, size, size);
      }}
    }}

    function tick(now) {{
      const interval = 1000 / Number(fpsInput.value);
      if (!paused && now - lastTick >= interval) {{
        frame = (frame + 1) % columns;
        lastTick = now;
        drawAll();
      }}
      requestAnimationFrame(tick);
    }}

    function build() {{
      for (const row of rows) {{
        const wrap = document.createElement('div');
        wrap.className = 'preview';
        const name = document.createElement('div');
        name.className = 'name';
        name.textContent = row.name;
        const canvas = document.createElement('canvas');
        wrap.append(name, canvas);
        stage.append(wrap);
        canvases.push({{ row: row.row, canvas }});
      }}
      drawAll();
      requestAnimationFrame(tick);
    }}

    fpsInput.addEventListener('input', () => {{
      fpsValue.textContent = fpsInput.value;
    }});
    scaleInput.addEventListener('input', () => {{
      scaleValue.textContent = `${{scaleInput.value}}x`;
      drawAll();
    }});
    toggle.addEventListener('click', () => {{
      paused = !paused;
      toggle.textContent = paused ? 'Play' : 'Pause';
    }});

    image.onload = build;
    image.src = atlasUrl;
  </script>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--atlas", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--rows", type=int, required=True)
    parser.add_argument("--columns", type=int, required=True)
    parser.add_argument("--cell", type=int, default=128)
    parser.add_argument("--row-names", default="")
    parser.add_argument("--title", default="PNG Loop Preview")
    parser.add_argument("--scale", type=int, default=2)
    parser.add_argument("--fps", type=int, default=10)
    args = parser.parse_args()

    atlas = Path(args.atlas).expanduser().resolve()
    output = Path(args.out).expanduser().resolve()
    row_names = [name.strip() for name in args.row_names.split(",") if name.strip()]
    if row_names and len(row_names) != args.rows:
        raise SystemExit(f"--row-names has {len(row_names)} names; expected {args.rows}")

    rows = [{"name": row_names[i] if row_names else f"row-{i:02d}", "row": i} for i in range(args.rows)]
    atlas_rel = os.path.relpath(atlas, output.parent).replace(os.sep, "/")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        HTML_TEMPLATE.format(
            title=args.title,
            atlas_url=json.dumps(atlas_rel),
            cell=args.cell,
            columns=args.columns,
            rows=json.dumps(rows, ensure_ascii=False),
            scale=args.scale,
            fps=args.fps,
        ),
        encoding="utf-8",
    )
    print(f"wrote {output}")


if __name__ == "__main__":
    main()
