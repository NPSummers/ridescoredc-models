from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_package_includes_optional_model_and_metadata(tmp_path):
    output = tmp_path / "out"
    distribution = tmp_path / "dist"
    output.mkdir()
    for name in (
        "road_segment",
        "crashes",
        "ridescore_v1_scores",
        "bna_stress_scores",
    ):
        (output / f"{name}.parquet").write_bytes(name.encode())
    (output / "metadata.json").write_text("{}")
    (output / "run.json").write_text(json.dumps({"run_date": "2026-09-30"}))
    subprocess.run(
        [
            sys.executable,
            str(Path(__file__).parents[1] / "scripts" / "make_package.py"),
            "--out",
            str(output),
            "--into",
            str(distribution),
            "--version",
            "0.1",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    package = distribution / "ridescoredc-data-preview-0.1"
    document = json.loads((package / "datapackage.json").read_text())
    resources = {resource["name"] for resource in document["resources"]}

    assert "bna_stress_scores" in resources
    assert document["metadata"] == "metadata.json"
    assert (package / "metadata.json").exists()
