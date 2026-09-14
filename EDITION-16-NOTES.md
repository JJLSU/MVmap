# Mount Vernon Estate Atlas, Edition 16

## Places

The Places list grows from 16 to 45. The original 16 remain the numbered highlights. Every other named building footprint inside the historic core (Salt House, Smokehouse, Spinning House, Storehouse and Clerk's Quarters, Wash House, Servants' Hall, Gardener's House, Stable, Coach House, Icehouse, Well House, Dung Repository, both Necessaries, both Garden Houses, the farm structures, the visitor facilities and so on) is appended as a minor place, grouped by category in the sidebar. Every place is routable and carries the same stable OpenStreetMap id and empty `audio_url` slot as before. Minor markers appear from zoom 18 and their labels from zoom 18.75, so the estate view stays legible. Unnamed footprints are not listed; if the estate can name them, they can be added the same way.

Every OpenStreetMap footprint in the tile bounds is already drawn on the ground tiles, so nothing was added to the artwork. Structures that Mount Vernon has and OpenStreetMap does not (the Paint Cellar beside the Mansion, the Pioneer Farm slave cabin, the treading-barn yard details) need aerial or plan reference before they can be traced.

## Tapping a building

Tapping a building footprint or a marker now opens a small card at the tap point with the name, its category, a Details button and an Add to route button. The map does not move. Details opens the full place card; on phones that card is a bottom sheet with a 44 px close control. Footprints are tappable at every zoom without switching on the reference building layer, with a wider hit tolerance on touch screens. On phones the legend, the map heading and the edition note no longer sit over the map, because they were intercepting taps on the buildings under them; the legend content remains in the map notes.

## Contrast

All 268 ground tiles were re-graded: gamma 1.22, saturation 1.18, contrast 1.22, with a slight shift away from yellow. Paths, walls, planting beds and tree shading now separate from turf on a phone screen outdoors. The garden vector layer and the legend swatches were graded with the same curve so they still match the tiles. The `tile_revision` is bumped to `ed16-graded`.

## Files

- `dist/app.js`, `dist/style.css`, `dist/index.html`: places, tap cards, phone layout, edition label and notes.
- `dist/baked/tiles/`: graded tiles.
- `source/grade.py`: the grading curve, runnable against any tile directory.

## 16.1

A stray rendered object sat on the lawn triangle north of the parkway roundabout (around 38.71191 N, 77.08591 W) at every zoom from 16 to 19. It is painted out. The object is still in the Blender scene; find it near that position and delete it before the next bake. All tiles also received a light unsharp mask (radius 1.2 px, amount 0.6) and are saved at WebP quality 90, which sharpens edges at zoom 20 and above without adding halos. Tile revision `ed16-1`.
