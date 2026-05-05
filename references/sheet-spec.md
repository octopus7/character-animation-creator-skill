# 128x128 Character Sheet Spec

## Default Combat Sheet

Cell size: fixed `128x128`.

Directions:

```text
south
south-east
east
north-east
north
north-west
west
south-west
```

Actions:

```text
idle: 4 frames, padded to 6 cells
walk: 6 frames
attack: 6 frames
```

Default row order:

```text
idle-south
idle-south-east
idle-east
idle-north-east
idle-north
idle-north-west
idle-west
idle-south-west
walk-south
walk-south-east
walk-east
walk-north-east
walk-north
walk-north-west
walk-west
walk-south-west
attack-south
attack-south-east
attack-east
attack-north-east
attack-north
attack-north-west
attack-west
attack-south-west
```

Default atlas: `768x3072`, 6 columns x 24 rows.

## Prompt Constraints

- no text, UI, labels, numbers, frame borders, or guide lines
- no shadows, floor marks, dust trails, or motion blur
- no detached VFX unless exported as a separate VFX sheet
- character must remain fully inside each `128x128` frame
- use the 128px cell density naturally with clean anime sprite detail
- avoid forced chunky pixel-art styling unless the user explicitly requests it
- keep readable silhouette while preserving facial features, hair shape, outfit detail, hands, and feet
- for final transparent output, prefer paired `#000000` and `#ffffff` background renders and derive alpha from the pair instead of using green chroma key

