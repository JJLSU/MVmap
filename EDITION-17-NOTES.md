# Mount Vernon Estate Atlas, Edition 17: fresh bake at higher resolution

## What changed

The ground tiles are rendered again from `Mount-Vernon-Edition14-Master.blend`, not patched from the previous tiles. Two Cycles renders were made on CPU: the whole estate at the original 4608 by 3411 pixels and the historic core at 6144 by 5135 pixels, double the earlier core bake. Both used 48 adaptive samples with OpenImageDenoise, rendered in horizontal strips of under three minutes each and stitched losslessly; the strips join without visible seams.

The pyramid now runs from zoom 14 to zoom 20. Zoom 20 exists only where the core render covers, 56 tiles at 8 pixels per metre. The tile loader draws each tile onto a canvas and, when a tile is missing, falls back to the matching quarter of its parent, so zooming past 19 outside the core shows upscaled zoom 19 rather than a hole. `maxNativeZoom` is 20.

The garden detail from Edition 15 is applied to the new tiles from `gardens-2026.geojson` at every zoom including 20, retired path strips are inpainted, and the Edition 16 contrast grade is applied, with a lighter sharpen than before because the new render needs less. The whole chain runs on lossless PNG and encodes once to WebP at quality 90. Tile revision `ed17`.

The `leisure=garden` polygon `way/1028542424` in the parkway roundabout triangle, which the scene builder turned into vegetable rows and which read as a black splotch, is hidden from the render (`hide_render` on its three objects). It is still in the scene; delete it in Blender if you prefer.

## Things to check

The master models the greenhouse roof in slate. The Edition 14 tiles that this replaces showed it red. The new bake follows the master.

The scene was opened with Blender 4.3.0 as a Python module; the file was saved by a slightly newer 4.3 build and Blender warned about possible data loss. The render matches the master visually, including the Mansion piazza, cupola and colonnades, and nothing in the material list is missing, but if anything looks off compared with a render on your machine, that is the first thing to suspect.

## Files

- `dist/baked/tiles/`: 324 tiles, zooms 14 to 20, 9.1 MB.
- `dist/projection.js`: canvas tile loader with parent fallback, `maxNativeZoom: 20`.
- `source/render/`: `setup_core.py`, `strip.py`, `batch.sh`, `tile_bake17.py`, `finalize.py`; the blend itself is not in the archive.
