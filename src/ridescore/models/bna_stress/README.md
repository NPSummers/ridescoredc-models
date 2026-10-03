# BNA segment stress

This optional model applies the segment-stress rules from `bikescore-bna` to the RideScore DC normalized DDOT street table. It writes `bna_stress_scores.parquet` beside the existing `ridescore_v1_scores.parquet` output.

## Output

The output has one row per pipeline `segment_id` and one model field:

- `segment_id`: the DDOT roadway block identifier.
- `bna_seg_stress`: `1` means comfortable and `3` means uncomfortable.

BNA's two-level scale is not equivalent to RideScore v1's four-level `lts_level` scale. Use the two models as separate measures and compare them at a coarse level.

## Field conversions

The adapter maps RideScore functional classes to OSM highway classes, maps RideScore bike facilities to BNA infrastructure values, and converts total DDOT lanes to per-direction lanes with `ceil(total lanes / 2)`.

The adapter currently leaves infrastructure width and the bicycle access tag missing. It takes the worse stress value of the two directions as the segment result.

## Limitations

- One-way streets can be misrepresented when total lanes are divided by two.
- DDOT does not provide bike-lane width in the form needed by the BNA rules.
- Intersection crossing stress is not included.
- BNA class adjustments are not included.
- `bikescore-bna` has not been fully validated for DC, so this output is a second opinion rather than ground truth.

## Reproduce

Install the optional dependency and run the committed fixture:

```bash
uv sync --extra bna
uv run ridescore build --cache tests/fixtures/snapshot --run-date 2026-08-05 --out out-fixture
uv run ridescore inspect --out out-fixture
```

The core pipeline remains usable without the optional extra. Without it, the BNA output is skipped and the existing RideScore v1 outputs are unchanged.
