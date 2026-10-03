from __future__ import annotations

import importlib.util

import geopandas as gpd
import pytest

from ridescore import build
from ridescore.models.bna_stress.score import score, to_bna_frame

pytestmark = pytest.mark.skipif(
    importlib.util.find_spec("bikescore_bna") is None,
    reason="requires the optional bna extra",
)


@pytest.fixture
def built(extract, run_date):
    return build.build(extract, run_date)


def test_to_bna_frame_maps_directional_inputs():
    segments = gpd.GeoDataFrame(
        {
            "function": ["Principal/Primary Arterial", "Local"],
            "speed_limit": [30, 20],
            "num_lanes": [3, 2],
            "bike_facility_type": ["protected_track", "painted_lane"],
        }
    )

    frame = to_bna_frame(segments)

    assert frame["adj_fc"].tolist() == ["primary", "residential"]
    assert frame["ft_lanes"].tolist() == [2, 1]
    assert frame["tf_lanes"].tolist() == [2, 1]
    assert frame["ft_bike_infra"].tolist() == ["track", "lane"]
    assert frame["tf_bike_infra"].tolist() == ["track", "lane"]


def test_score_returns_two_level_segment_stress(built):
    result = score(built.road_segment)

    assert result.index.equals(built.road_segment.index)
    assert result.columns.tolist() == ["bna_seg_stress"]
    assert set(result["bna_seg_stress"]) <= {1, 3}


def test_build_writes_bna_scores_when_dependency_is_installed(built, tmp_path):
    assert built.bna_stress_scores is not None
    assert built.bna_stress_scores["segment_id"].is_unique
    assert set(built.bna_stress_scores["segment_id"]) == set(
        built.road_segment["segment_id"]
    )

    written = build.write(built, tmp_path)

    assert "bna_stress_scores" in written
    assert len(build.read(tmp_path, "bna_stress_scores")) == len(built.road_segment)
