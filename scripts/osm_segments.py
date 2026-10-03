from __future__ import annotations

import sys
from pathlib import Path

import geopandas as gpd
from bikescore_bna import build_config, discover_inputs, run_stage
from bikescore_bna.pipeline import PIPELINE


def main(datasets_dir: Path, output_dir: Path) -> None:
    inputs = discover_inputs(datasets_dir)
    config = build_config("default")
    stages = {stage.name: stage for stage in PIPELINE}
    completed = {}

    for name in ("parse", "attributes", "segment"):
        stage_dir = output_dir / name
        stage_dir.mkdir(parents=True, exist_ok=True)
        run_stage(stages[name], completed, inputs, stage_dir, config)
        completed[name] = stage_dir

    segments = gpd.read_parquet(output_dir / "segment" / "segments.parquet")
    print(f"{len(segments)} segments from {segments['osm_id'].nunique()} OSM ways")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
