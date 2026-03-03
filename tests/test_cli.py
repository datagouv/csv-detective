import json
import shutil
import subprocess
import sys

import pytest


@pytest.fixture
def csv_detective_bin():
    """Resolve the csv_detective console script path."""
    path = shutil.which("csv_detective")
    if path is None:
        pytest.skip("csv_detective CLI not installed")
    return path


def test_cli_runs_on_csv(csv_detective_bin):
    """E2E: the CLI should analyze a CSV file and return valid JSON."""
    result = subprocess.run(
        [csv_detective_bin, "tests/data/a_test_file.csv"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"CLI failed with stderr:\n{result.stderr}"
    output = json.loads(result.stdout)
    assert isinstance(output, dict)
    assert output["separator"] == ";"
    assert "columns" in output


def test_cli_with_num_rows(csv_detective_bin):
    """E2E: the CLI should accept the -n option."""
    result = subprocess.run(
        [csv_detective_bin, "tests/data/b_test_file.csv", "-n", "5"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"CLI failed with stderr:\n{result.stderr}"
    output = json.loads(result.stdout)
    assert isinstance(output, dict)
    assert "columns" in output


def test_cli_missing_file(csv_detective_bin):
    """E2E: the CLI should fail with a non-zero exit code for a missing file."""
    result = subprocess.run(
        [csv_detective_bin, "nonexistent_file.csv"],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


def test_cli_no_args(csv_detective_bin):
    """E2E: the CLI should fail when called without arguments."""
    result = subprocess.run(
        [csv_detective_bin],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "usage" in result.stderr.lower() or "error" in result.stderr.lower()
