"""Slow end-to-end performance canary for csv-detective.

Excluded from default CI via ``pytest -m "not slow"``. Run manually or via the
CircleCI ``benchmark-workflow`` (pipeline parameter ``run-benchmarks=true``).
"""

import csv
import json
import os
import statistics
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from random import Random
from time import perf_counter

import pytest

from csv_detective import routine

NB_ROWS = 500_000
NB_RUNS = 3
BENCHMARK_DIR = Path(".benchmarks")
BENCHMARK_JSON = BENCHMARK_DIR / "benchmark.json"


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
    communes = [
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
    start = date(2020, 1, 1)

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(
            [
                "id",
                "amount",
                "ratio",
                "event_date",
                "commune",
                "siren",
                "description",
                "latitude",
                "longitude",
                "code_postal",
            ]
        )
        for i in range(nb_rows):
            writer.writerow(
                [
                    i,
                    rng.randint(0, 1_000_000),
                    round(rng.uniform(0, 100), 2),
                    (start + timedelta(days=rng.randint(0, 1500))).isoformat(),
                    rng.choice(communes),
                    f"{rng.randint(100_000_000, 999_999_999)}",
                    f"row-{i}-note-{rng.randint(0, 9999)}",
                    round(rng.uniform(41.0, 51.0), 6),
                    round(rng.uniform(-5.0, 10.0), 6),
                    f"{rng.randint(1000, 95999):05d}",
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
        durations.append(perf_counter() - start)
    assert analysis is not None
    return analysis, durations


@pytest.fixture(scope="module")
def benchmark_csv(tmp_path_factory: pytest.TempPathFactory) -> Path:
    path = tmp_path_factory.mktemp("benchmark") / "benchmark_input.csv"
    _generate_benchmark_csv(path)
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

    assert analysis["total_lines"] == NB_ROWS
    assert analysis["columns"]
    assert analysis["header"]
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
