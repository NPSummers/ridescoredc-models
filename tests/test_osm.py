from __future__ import annotations

import geopandas as gpd
import pandas as pd

from ridescore.sources.osm import to_ridescore


def test_osm_segments_map_to_the_ridescore_contract():
    segments = gpd.GeoDataFrame(
        {
            "osm_id": [101, 102],
            "start_node_id": [1, 2],
            "end_node_id": [2, 3],
            "functional_class": ["primary", "residential"],
            "speed_limit": [35, 25],
            "ft_lanes": [2, 1],
            "tf_lanes": [2, 1],
            "ft_bike_infra": ["track", None],
            "tf_bike_infra": [None, "lane"],
            "ft_lanes_imputed": [False, True],
            "tf_lanes_imputed": [False, True],
            "width_ft": [40.0, pd.NA],
        },
        geometry=gpd.GeoSeries.from_wkt(
            [
                "LINESTRING (-77 38.9, -77 38.901)",
                "LINESTRING (-77 38.901, -77 38.902)",
            ]
        ),
        crs="EPSG:4326",
    )

    result = to_ridescore(segments)

    assert result["segment_id"].tolist() == ["101:1-2", "102:2-3"]
    assert result["function"].tolist() == ["Principal/Primary Arterial", "Local"]
    assert result["num_lanes"].tolist() == [4, 2]
    assert result["num_lanes_raw"].notna().tolist() == [True, False]
    assert result["bike_facility_type"].tolist() == ["protected_track", "painted_lane"]
    assert result["pavement_condition"].isna().all()
    assert result["crash_count_5yr"].tolist() == [0, 0]
