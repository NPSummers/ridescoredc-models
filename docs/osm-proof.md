# OSM base-map proof

This proof runs the OSM parsing, attribute, and segmentation stages on a committed-code synthetic grid and converts the result to the street-table contract used by the RideScore models.

It does not fetch real OSM data. It is the safe first step before adding a full-city OSM source to the production pipeline.

## Run it

```bash
uv sync --extra bna
uv run --extra bna python scripts/make_osm_fixture.py raw/osm-synthetic
uv run --extra bna python scripts/osm_segments.py raw/osm-synthetic raw/osm-synthetic-run
```

The expected result is 12 segments from 6 OSM ways. The segment output is written to `raw/osm-synthetic-run/segment/segments.parquet`.

The durable-key candidate is `osm_id:start_node_id-end_node_id`. The library's row-number identifiers are not used.

## RideScore adapter

`ridescore.sources.osm.to_ridescore` maps OSM functional classes, speed, directional lanes, and directional bike infrastructure to the columns consumed by the existing scoring model. It leaves pavement condition missing and sets crash counts to zero for this proof; a real source must run the pipeline crash join on the OSM geometries.

The full-city OSM replacement remains a separate follow-up because it requires a dated regional extract, boundary handling, crash joining, and comparison against the DDOT-based network.
