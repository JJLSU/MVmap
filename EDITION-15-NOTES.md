# Mount Vernon Estate Atlas, Edition 15: garden detail

## What changed

Edition 14 drew the insides of the four gardens from OpenStreetMap footways and boundaries. Against the aerial imagery, several of those lines were in the wrong place, several ran through planting beds, and several were walls or fences rather than paths. Edition 15 replaces that content.

Upper Garden. The perimeter walks, the wide cross walk, the three north-south walks, the south walk and the greenhouse forecourt are traced from the imagery. The enclosure is drawn as brick wall from the Garden House to the greenhouse and along the Bowling Green side, with the greenhouse itself closing the north-east side. The two parterres, the three box-edged vegetable compartments and the north lawn are drawn as compartments. Source footways that sat two to four metres off the real walks in the south of the garden are retired.

Lower Garden. The wall is drawn on every side, with openings beside the Garden House, at the north-east corner and at the south-east corner. The gravel perimeter walks, the upper gravel walk, the central grass walk, the cross walks, the parterre square with its diagonal walks and roundel, the cold frames and the compartments are traced from the imagery. The interpreted diagonal "central walk" of Edition 14 is gone; it did not exist.

Fruit Garden and Nursery. The post-and-rail perimeter fence and the dividing fence between the vegetable plots and the orchard are drawn as fences. Only two paths exist inside: the gravel cross walk (with gates through the west and east fences) and the north walk. The eight vegetable plots and the three orchard quarters are drawn as compartments. The sheep pen worm fence west of the garden is traced.

Pioneer Farm. Worm fences now line both sides of the field lane and the outer edges of the fields, and the eight crop fields and the kitchen garden are drawn between them. The lanes themselves keep their mapped geometry, because the oblique farm imagery does not register to the map within a few metres; the fence and field layout is placed relative to the lanes.

## How it was done

Each aerial was georeferenced to the map with control points on mapped buildings and fence corners (greenhouse ends and Garden House for the Upper Garden, the two garden houses for the Lower Garden, the four fence corners and the path junction for the Fruit Garden). Residuals are under 0.5 m for the Upper and Lower Gardens and about 1 to 2.5 m for the Fruit Garden. Geometry was traced in image pixels and transformed into the map frame.

The result lives in `dist/gardens-2026.geojson` (and `dist/gardens.js`). Three things are built from it:

1. The baked ground tiles inside each enclosure were re-rendered at every zoom level in the existing style (turf, striped beds, gravel walks, box hedges, wall with oblique shadow, fence posts, worm-fence zigzags, orchard rings, crop rows). Retired path strips just outside the enclosures were inpainted from their surroundings.
2. An always-on vector layer draws the walks, walls, fences and hedges in metre-true widths that rescale with zoom, with hover labels. It can be switched off under Layers.
3. The routing graph drops the retired footways, adds the pre-noded garden walks, and connects them to the estate network only at gates.

## Still open

Nothing here is surveyed. Gate positions are read from imagery. The Lower Garden's north-west wall line is under tree canopy and follows the mapped line there. The Fruit Garden sits about a metre or two off in places because the imagery does not register perfectly. The Pioneer Farm layout is schematic relative to the lanes. All of this is flagged in the map notes and in `getNavigationContext()`.

## Files

- `dist/gardens-2026.geojson`, `dist/gardens.js`: the garden detail.
- `dist/baked/tiles/`: 28 re-rendered tiles across zooms 14 to 19; `tile_revision` bumped so cached tiles refresh.
- `dist/app.js`, `dist/index.html`, `dist/AI-INTEGRATION.md`: integration, notes, edition label.
- `source/`: the tracing and rendering scripts and the aerial reference images, so the gardens can be re-traced or re-rendered.
