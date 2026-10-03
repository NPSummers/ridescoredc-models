from __future__ import annotations

import json
import sys
from pathlib import Path

import osmium


def main(output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    lon0, lat0, spacing = -77.040, 38.900, 0.0012
    nodes = {(row, column): 1 + row * 3 + column for row in range(3) for column in range(3)}
    writer = osmium.SimpleWriter(str(output / "osm-grid.pbf"))

    for (row, column), node_id in nodes.items():
        writer.add_node(
            osmium.osm.mutable.Node(
                id=node_id,
                location=(lon0 + column * spacing, lat0 + row * spacing),
                tags={},
                version=1,
                timestamp="2026-01-01T00:00:00Z",
            )
        )

    ways = [
        (101, [(0, 0), (0, 1), (0, 2)], {"highway": "residential", "maxspeed": "25 mph"}),
        (
            102,
            [(1, 0), (1, 1), (1, 2)],
            {"highway": "secondary", "lanes": "2", "maxspeed": "30 mph", "cycleway": "lane"},
        ),
        (103, [(2, 0), (2, 1), (2, 2)], {"highway": "residential"}),
        (201, [(0, 0), (1, 0), (2, 0)], {"highway": "tertiary", "lanes": "2"}),
        (202, [(0, 1), (1, 1), (2, 1)], {"highway": "residential", "maxspeed": "20 mph"}),
        (
            203,
            [(0, 2), (1, 2), (2, 2)],
            {"highway": "primary", "lanes": "4", "maxspeed": "35 mph", "cycleway": "track"},
        ),
    ]
    for way_id, cells, tags in ways:
        writer.add_way(
            osmium.osm.mutable.Way(
                id=way_id,
                nodes=[nodes[cell] for cell in cells],
                tags=tags,
                version=1,
                timestamp="2026-01-01T00:00:00Z",
            )
        )
    writer.close()

    padding = 0.003
    bounds = [
        lon0 - padding,
        lat0 - padding,
        lon0 + 2 * spacing + padding,
        lat0 + 2 * spacing + padding,
    ]
    ring = [
        [bounds[0], bounds[1]],
        [bounds[2], bounds[1]],
        [bounds[2], bounds[3]],
        [bounds[0], bounds[3]],
        [bounds[0], bounds[1]],
    ]
    boundary = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {},
                "geometry": {"type": "Polygon", "coordinates": [ring]},
            }
        ],
    }
    (output / "boundary-grid.geojson").write_text(json.dumps(boundary))


if __name__ == "__main__":
    main(Path(sys.argv[1]))
