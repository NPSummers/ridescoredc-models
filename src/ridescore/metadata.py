from __future__ import annotations

from collections.abc import Iterable

SCHEMA_VERSION = 1
METADATA_FILENAME = "metadata.json"

DATASET_INFO = {
    "road_segment": {
        "description": "The published roadway network and normalized street attributes.",
        "row_grain": "one roadway block",
        "source": "DC Open Data roadway blocks, cyclist crashes, and the DC boundary",
    },
    "crashes": {
        "description": "Cyclist crashes included in the pipeline run.",
        "row_grain": "one cyclist crash",
        "source": "DC Open Data cyclist crash records",
    },
    "ridescore_v1_scores": {
        "description": "The published RideScore v1 component scores and blend.",
        "row_grain": "one roadway block",
        "model": "ridescore_v1",
    },
    "bna_stress_scores": {
        "description": "BNA-derived segment stress as an optional second model.",
        "row_grain": "one roadway block",
        "model": "bikescore-bna segment stress",
    },
}

FIELD_INFO = {
    "segment_id": {
        "description": "The durable identifier used to join scores to a roadway block.",
        "source_field": "BLOCKKEY",
    },
    "tile_id": {
        "description": "Integer feature identifier assigned for map rendering.",
        "lifetime": "one build",
    },
    "speed_limit": {"description": "Filled posted speed limit.", "unit": "mph"},
    "speed_limit_raw": {
        "description": "Posted speed limit before filling missing values.",
        "unit": "mph",
    },
    "num_lanes": {"description": "Filled total travel lane count."},
    "num_lanes_raw": {"description": "Total travel lane count before filling missing values."},
    "bike_facility_type": {
        "description": "Normalized bicycle facility classification.",
        "expected_values": ["none", "painted_lane", "buffered_lane", "protected_track"],
    },
    "len": {"description": "Street segment length.", "unit": "metres"},
    "crash_count_5yr": {
        "description": "Cyclist crashes joined to the segment in the run's five-year window.",
        "unit": "crashes",
    },
    "serious_injury_count_5yr": {
        "description": "Serious cyclist injuries in the five-year window."
    },
    "fatal_count_5yr": {"description": "Cyclist fatalities in the five-year window."},
    "lts_level": {
        "description": "RideScore v1 Level of Traffic Stress.",
        "expected_values": [1, 2, 3, 4],
    },
    "ridescore_v1": {
        "description": "RideScore v1 blended score; higher is safer under the published blend.",
        "unit": "score from 0 to 100",
    },
    "bna_seg_stress": {
        "description": "BNA segment stress; 1 is comfortable and 3 is uncomfortable.",
        "expected_values": [1, 3],
    },
}


def _column_info(values) -> dict:
    info = {
        "dtype": str(values.dtype),
        "nullable": bool(values.isna().any()),
    }
    info.update(FIELD_INFO.get(values.name, {}))
    return info


def describe(built) -> dict:
    frames = {
        "road_segment": built.road_segment,
        "crashes": built.crashes,
        "ridescore_v1_scores": built.ridescore_v1_scores,
    }
    if built.bna_stress_scores is not None:
        frames["bna_stress_scores"] = built.bna_stress_scores

    datasets = {}
    for name, frame in frames.items():
        description = dict(DATASET_INFO[name])
        description["row_count"] = len(frame)
        description["columns"] = {
            column: _column_info(frame[column]) for column in frame.columns
        }
        datasets[name] = description

    return {
        "schema_version": SCHEMA_VERSION,
        "run_date": built.derived.get("run_date"),
        "crash_window": built.derived.get("crash_window"),
        "datasets": datasets,
    }


def validate(document: dict, dataset_names: Iterable[str]) -> None:
    if document.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("metadata has an unsupported schema version")
    datasets = document.get("datasets")
    if not isinstance(datasets, dict):
        raise ValueError("metadata has no datasets object")
    missing = set(dataset_names) - datasets.keys()
    if missing:
        raise ValueError(f"metadata is missing datasets: {', '.join(sorted(missing))}")
    for name in dataset_names:
        if not datasets[name].get("columns"):
            raise ValueError(f"metadata has no columns for {name}")
