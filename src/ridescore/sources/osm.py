from __future__ import annotations

import geopandas as gpd
import pandas as pd

OSM_TO_FUNCTION = {
    "motorway": "Other Freeway and Expressway",
    "motorway_link": "Other Freeway and Expressway",
    "trunk": "Other Freeway and Expressway",
    "trunk_link": "Other Freeway and Expressway",
    "primary": "Principal/Primary Arterial",
    "primary_link": "Principal/Primary Arterial",
    "secondary": "Minor Arterial",
    "secondary_link": "Minor Arterial",
    "tertiary": "Collector",
    "tertiary_link": "Collector",
    "residential": "Local",
    "unclassified": "Local",
    "living_street": "Local",
}

INFRA_TO_FACILITY = {
    "track": "protected_track",
    "buffered_lane": "buffered_lane",
    "lane": "painted_lane",
}

FACILITY_RANK = {
    "none": 0,
    "painted_lane": 1,
    "buffered_lane": 2,
    "protected_track": 3,
}


def _best_facility(ft: pd.Series, tf: pd.Series) -> pd.Series:
    directions = pd.concat(
        [ft.map(INFRA_TO_FACILITY), tf.map(INFRA_TO_FACILITY)], axis=1
    ).fillna("none")
    ranks = directions.replace(FACILITY_RANK)
    return directions.where(ranks.eq(ranks.max(axis=1), axis=0)).bfill(axis=1).iloc[:, 0]


def to_ridescore(segments: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    out = gpd.GeoDataFrame(index=segments.index, geometry=segments.geometry, crs=segments.crs)
    out["segment_id"] = (
        segments["osm_id"].astype(str)
        + ":"
        + segments["start_node_id"].astype(str)
        + "-"
        + segments["end_node_id"].astype(str)
    )
    out["function"] = segments["functional_class"].map(OSM_TO_FUNCTION).fillna("Other")
    out["speed_limit"] = segments["speed_limit"].astype(int)
    out["num_lanes"] = (
        segments["ft_lanes"].fillna(0) + segments["tf_lanes"].fillna(0)
    ).astype(int)
    imputed = segments.get("ft_lanes_imputed", False) | segments.get(
        "tf_lanes_imputed", False
    )
    out["num_lanes_raw"] = out["num_lanes"].where(~imputed, pd.NA)
    out["bike_facility_type"] = _best_facility(
        segments["ft_bike_infra"], segments["tf_bike_infra"]
    )
    out["road_width"] = segments.get("width_ft")
    out["pavement_condition"] = None
    out["crash_count_5yr"] = 0
    return out


__all__ = ["to_ridescore"]
