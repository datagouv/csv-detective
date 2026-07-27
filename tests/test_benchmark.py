"""Slow end-to-end performance canary for csv-detective.

Excluded from default CI via ``pytest -m "not slow"``. Run manually or via the
CircleCI ``benchmark-workflow`` (pipeline parameter ``run-benchmarks=true``).
"""

import csv
import json
import os
import statistics
import sys
from collections.abc import Callable
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from random import Random
from time import perf_counter

import pytest

from csv_detective import routine
from csv_detective.parsing.csv import CHUNK_SIZE

NB_ROWS = 500_000
NB_RUNS = 3
BENCHMARK_DIR = Path(".benchmarks")
BENCHMARK_JSON = BENCHMARK_DIR / "benchmark.json"

VALID_COMMUNES = [
    "Paris",
    "Lyon",
    "Marseille",
    "Toulouse",
    "Nice",
    "Nantes",
    "Montpellier",
    "Strasbourg",
    "Bordeaux",
    "Lille",
]
VALID_POSTCODES = [
    "75020",
    "01000",
    "13001",
    "69001",
    "33000",
    "59000",
    "44000",
    "67000",
    "34000",
    "06000",
]
INVALID_POSTCODES = ["77777", "00000", "99999"]
VALID_DEPARTMENTS = ["75", "69", "13", "33", "59", "67", "44", "06", "2A", "974"]
INVALID_COMMUNE = "Unknown"


def _siren_luhn_check_digit(prefix: str) -> str:
    """Return the 9th digit that satisfies the SIREN Luhn key for an 8-digit prefix."""
    for check in range(10):
        candidate = f"{prefix}{check}"
        cle = 0
        pair = False
        for digit in candidate:
            y = int(digit) * (1 + pair)
            cle += y // 10 + y % 10
            pair = not pair
        if cle % 10 == 0:
            return str(check)
    raise ValueError(f"Could not compute SIREN check digit for prefix {prefix}")


def _random_valid_siren(rng: Random) -> str:
    prefix = f"{rng.randint(0, 99_999_999):08d}"
    return prefix + _siren_luhn_check_digit(prefix)


def _pick_mostly_valid(
    rng: Random,
    *,
    valid: Callable[[], str],
    invalid: Callable[[], str],
    invalid_rate: float,
) -> str:
    if rng.random() < invalid_rate:
        return invalid()
    return valid()


def _runner_cpu() -> str:
    if cpu := os.environ.get("BENCHMARK_RUNNER_CPU"):
        return cpu
    return str(os.cpu_count() or "")


def _runner_memory_mb() -> str:
    if memory := os.environ.get("BENCHMARK_RUNNER_MEMORY_MB"):
        return memory
    try:
        pages = os.sysconf("SC_PHYS_PAGES")
        page_size = os.sysconf("SC_PAGE_SIZE")
        if pages > 0 and page_size > 0:
            return str((pages * page_size) // (1024 * 1024))
    except (AttributeError, OSError, ValueError):
        pass
    return ""


def _generate_benchmark_csv(path: Path, nb_rows: int = NB_ROWS, seed: int = 42) -> None:
    """Generate a reproducible mixed-type CSV large enough to exercise chunking."""
    rng = Random(seed)
    start = date(2020, 1, 1)

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(
            [
                "id",
                "amount",
                "quantity",
                "ratio",
                "event_date",
                "event_datetime",
                "commune",
                "ville",
                "siren",
                "org_id",
                "departement",
                "code_postal",
                "optional_note",
                "description",
                "latitude",
                "longitude",
            ]
        )
        for i in range(nb_rows):
            event_day = start + timedelta(days=rng.randint(0, 1500))
            event_dt = datetime.combine(event_day, datetime.min.time()) + timedelta(
                hours=rng.randint(0, 23),
                minutes=rng.randint(0, 59),
                seconds=rng.randint(0, 59),
            )
            writer.writerow(
                [
                    i,
                    rng.randint(0, 1_000_000),
                    _pick_mostly_valid(
                        rng,
                        valid=lambda: str(rng.randint(1, 9999)),
                        invalid=lambda: "bad",
                        invalid_rate=0.02,
                    ),
                    round(rng.uniform(0, 100), 2),
                    event_day.isoformat(),
                    event_dt.strftime("%Y-%m-%d %H:%M:%S"),
                    rng.choice(VALID_COMMUNES),
                    _pick_mostly_valid(
                        rng,
                        valid=lambda: rng.choice(VALID_COMMUNES),
                        invalid=lambda: INVALID_COMMUNE,
                        invalid_rate=0.15,
                    ),
                    _random_valid_siren(rng),
                    _random_valid_siren(rng),
                    rng.choice(VALID_DEPARTMENTS),
                    _pick_mostly_valid(
                        rng,
                        valid=lambda: rng.choice(VALID_POSTCODES),
                        invalid=lambda: rng.choice(INVALID_POSTCODES),
                        invalid_rate=0.08,
                    ),
                    "" if rng.random() < 0.30 else f"note-{rng.randint(0, 9999)}",
                    f"row-{i}-note-{rng.randint(0, 9999)}",
                    round(rng.uniform(41.0, 51.0), 6),
                    round(rng.uniform(-5.0, 10.0), 6),
                ]
            )


def _median_seconds(durations: list[float]) -> float:
    return round(statistics.median(durations), 3)


def _write_scenario_result(
    *,
    test_name: str,
    input_file: str,
    durations: list[float],
    nb_rows: int,
) -> dict:
    """Merge this scenario into the run report JSON and return the scenario payload."""
    BENCHMARK_DIR.mkdir(parents=True, exist_ok=True)
    if BENCHMARK_JSON.exists():
        report = json.loads(BENCHMARK_JSON.read_text(encoding="utf-8"))
    else:
        report = {
            "datetime": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "ci": os.environ.get("BENCHMARK_CI", "local"),
            "commit_id": os.environ.get("CIRCLE_SHA1", "")[:7],
            "runner_class": os.environ.get("BENCHMARK_RUNNER_CLASS", ""),
            "runner_cpu": _runner_cpu(),
            "runner_memory_mb": _runner_memory_mb(),
            "python_version": os.environ.get(
                "BENCHMARK_PYTHON_VERSION",
                f"{sys.version_info.major}.{sys.version_info.minor}",
            ),
            "nb_rows": nb_rows,
            "input_file": input_file,
            "scenarios": [],
        }

    scenario = {
        "test_name": test_name,
        "runs_seconds": [round(d, 3) for d in durations],
        "execution_time_seconds": _median_seconds(durations),
        "nb_runs": NB_RUNS,
    }
    report["scenarios"] = [s for s in report["scenarios"] if s["test_name"] != test_name]
    report["scenarios"].append(scenario)
    BENCHMARK_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return scenario


def _run_timed_routine(file_path: str, *, output_profile: bool) -> tuple[dict, list[float]]:
    durations: list[float] = []
    analysis: dict | None = None
    for _ in range(NB_RUNS):
        start = perf_counter()
        analysis = routine(
            file_path=file_path,
            num_rows=-1,
            output_profile=output_profile,
            save_results=False,
        )
        assert analysis is not None
        durations.append(perf_counter() - start)
    return analysis, durations


def _assert_benchmark_detections(analysis: dict, *, output_profile: bool) -> None:
    columns = analysis["columns"]
    assert columns["event_date"]["format"] == "date"
    assert columns["event_datetime"]["format"] == "datetime_naive"
    assert columns["commune"]["format"] == "commune"
    assert columns["ville"]["format"] == "commune"
    assert columns["siren"]["format"] == "siren"
    assert columns["org_id"]["format"] != "siren"
    assert columns["departement"]["format"] == "code_departement"
    assert columns["code_postal"]["format"] == "code_postal"
    assert columns["quantity"]["format"] == "string"
    if output_profile:
        assert analysis["profile"]["optional_note"]["nb_missing_values"] > 0


@pytest.fixture(scope="module")
def benchmark_csv(tmp_path_factory: pytest.TempPathFactory) -> Path:
    path = tmp_path_factory.mktemp("benchmark") / "benchmark_input.csv"
    _generate_benchmark_csv(path)
    with path.open(encoding="utf-8") as f:
        assert sum(1 for _ in f) - 1 == NB_ROWS
    return path


@pytest.mark.slow
@pytest.mark.parametrize(
    "output_profile,test_name",
    [
        (False, "test_routine_big_file"),
        (True, "test_routine_big_file_with_profile"),
    ],
)
def test_routine_big_file(benchmark_csv: Path, output_profile: bool, test_name: str):
    analysis, durations = _run_timed_routine(
        str(benchmark_csv),
        output_profile=output_profile,
    )

    # Format detection may stop reading before EOF once every column is resolved
    # (see test_col_chunks early stop); total_lines is rows processed, not file size.
    assert CHUNK_SIZE <= analysis["total_lines"] <= NB_ROWS
    assert analysis["columns"]
    assert analysis["header"]
    _assert_benchmark_detections(analysis, output_profile=output_profile)
    if output_profile:
        assert "profile" in analysis

    scenario = _write_scenario_result(
        test_name=test_name,
        input_file=benchmark_csv.name,
        durations=durations,
        nb_rows=NB_ROWS,
    )
    print(
        f"{test_name}: runs={scenario['runs_seconds']!r} "
        f"median={scenario['execution_time_seconds']}s "
        f"(nb_rows={NB_ROWS}, output_profile={output_profile})"
    )
