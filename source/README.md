# Garden detail pipeline (Edition 15)

Scripts expect the repository layout `dist/` beside `source/` and read `dist/estate.geojson`, `dist/landscape-2025.geojson` and `dist/baked/projection.json`. Paths inside the scripts point at `/home/claude/mv/...`; adjust them for another machine.

1. `trace_upper.py`, `trace_lower.py`, `trace_fruit.py`: geometry traced in pixel coordinates of the four aerial screenshots (kept out of the archive for size; drop them into `source/ref/` as upper.png, lower.png, fruit.png, farm.png). `grid.py` renders a labelled pixel grid over an image for reading coordinates. `check.py <garden>` draws a trace over its aerial.
2. `build_gardens.py`: fits the image-to-map transforms (control points listed inside), converts traces to lon/lat, and builds the Pioneer Farm from the mapped lanes via `farm_build.py`. Writes `dist/gardens-2026.geojson`.
3. `network.py`: nodes the walk network, lists superseded OpenStreetMap ways and barriers, builds gate connectors. Rewrites `dist/gardens-2026.geojson` and `dist/gardens.js`.
4. `process.py <outdir> <zooms> [<gardens>]`: re-renders the baked tiles inside each enclosure using `render.py`, inpaints retired path strips, and writes WebP tiles. `preview.py` stitches a garden view from an output directory for inspection. `check_tiles.py` draws the GeoJSON over the tiles.

`sprite0.png` and `sprite1.png` are canopy sprites cut from the existing bake for trees drawn inside the gardens.
