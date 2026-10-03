from __future__ import annotations

import pandas as pd

FUNCTION_TO_OSM = {
    "Interstate": "motorway",
    "Other Freeway and Expressway": "motorway",
    "Principal/Primary Arterial": "primary",
    "Minor Arterial": "secondary",
    "Collector": "tertiary",
    "Local": "residential",
    "Other": "unclassified",
}

FACILITY_TO_INFRA = {
    "protected_track": "track",
    "buffered_lane": "buffered_lane",
    "painted_lane": "lane",
}


def to_bna_frame(segments: pd.DataFrame) -> pd.DataFrame:
    frame = pd.DataFrame(index=segments.index)
    frame["adj_fc"] = segments["function"].map(FUNCTION_TO_OSM).fillna("unclassified")
    frame["speed_limit"] = segments["speed_limit"].astype(int)

    per_direction = ((segments["num_lanes"].astype(int) + 1) // 2).astype(int)
    for direction in ("ft", "tf"):
        frame[f"{direction}_lanes"] = per_direction
        frame[f"{direction}_bike_infra"] = segments["bike_facility_type"].map(
            FACILITY_TO_INFRA
        )
        frame[f"{direction}_bike_infra_width"] = float("nan")

    frame["bicycle"] = None
    return frame


def score(segments: pd.DataFrame, scenario: str = "default") -> pd.DataFrame:
    from bikescore_bna import build_config

    config = build_config(scenario)
    stressed = config.stress.segment_rules.apply(
        to_bna_frame(segments), variables=config.variables
    )

    result = pd.DataFrame(index=segments.index)
    result["bna_seg_stress"] = stressed[["ft_seg_stress", "tf_seg_stress"]].max(axis=1).astype(int)
    return result


__all__ = ["FACILITY_TO_INFRA", "FUNCTION_TO_OSM", "score", "to_bna_frame"]
