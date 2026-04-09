#!/usr/bin/env python3
"""Compare csv-detective Python vs Rust outputs on test files."""

import json
import subprocess
import sys
import time
from pathlib import Path

TEST_DIR = Path("test_files")
RUST_BIN = Path("rust/target/release/csv-detective-rs")

SKIP_KEYS = {"columns_fields", "columns_labels"}

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BOLD = "\033[1m"
RESET = "\033[0m"


def run_python(file_path: Path) -> tuple[dict, float]:
    start = time.perf_counter()
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            f"import json; from csv_detective.explore_csv import routine; "
            f"print(json.dumps(routine('{file_path}', save_results=False), default=str))",
        ],
        capture_output=True,
        text=True,
    )
    elapsed = time.perf_counter() - start
    if result.returncode != 0:
        raise RuntimeError(f"Python failed: {result.stderr}")
    return json.loads(result.stdout), elapsed


def run_rust(file_path: Path) -> tuple[dict, float]:
    start = time.perf_counter()
    result = subprocess.run(
        [str(RUST_BIN), str(file_path)],
        capture_output=True,
        text=True,
    )
    elapsed = time.perf_counter() - start
    if result.returncode != 0:
        raise RuntimeError(f"Rust failed: {result.stderr}")
    return json.loads(result.stdout), elapsed


def normalize_value(v):
    """Normalize numpy int/float serialized as strings back to numbers."""
    if isinstance(v, str):
        try:
            if "." in v:
                return float(v)
            return int(v)
        except ValueError:
            pass
    return v


def diff_json(python_result, rust_result, path: str = "") -> list[str]:
    python_result = normalize_value(python_result)
    rust_result = normalize_value(rust_result)
    diffs = []

    if isinstance(python_result, dict) and isinstance(rust_result, dict):
        all_keys = set(python_result.keys()) | set(rust_result.keys())
        for key in sorted(all_keys):
            full_path = f"{path}.{key}" if path else key
            if key not in python_result:
                diffs.append(f"  {YELLOW}+ Rust has extra key: {full_path}{RESET}")
            elif key not in rust_result:
                diffs.append(f"  {RED}- Rust missing key: {full_path}{RESET}")
            else:
                diffs.extend(
                    diff_json(python_result[key], rust_result[key], full_path)
                )
    elif isinstance(python_result, list) and isinstance(rust_result, list):
        if len(python_result) != len(rust_result):
            diffs.append(
                f"  {RED}List length differs at {path}: "
                f"Python={len(python_result)} Rust={len(rust_result)}{RESET}"
            )
        for i, (pv, rv) in enumerate(zip(python_result, rust_result)):
            diffs.extend(diff_json(pv, rv, f"{path}[{i}]"))
    else:
        if python_result != rust_result:
            py_str = json.dumps(python_result, default=str)
            rs_str = json.dumps(rust_result, default=str)
            if len(py_str) > 80:
                py_str = py_str[:80] + "..."
            if len(rs_str) > 80:
                rs_str = rs_str[:80] + "..."
            diffs.append(
                f"  {RED}Value differs at {path}:{RESET}\n"
                f"    Python: {py_str}\n"
                f"    Rust:   {rs_str}"
            )

    return diffs


def main():
    if not RUST_BIN.exists():
        print(f"Building Rust binary (release)...")
        result = subprocess.run(
            ["cargo", "build", "--release", "--manifest-path", "rust/Cargo.toml"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"Cargo build failed:\n{result.stderr}")
            sys.exit(1)

    test_files = sorted(TEST_DIR.glob("*"))
    test_files = [f for f in test_files if f.is_file()]

    if not test_files:
        print(f"No test files found in {TEST_DIR}/")
        sys.exit(1)

    print(f"\n{BOLD}Comparing csv-detective Python vs Rust on {len(test_files)} files{RESET}\n")
    print(f"{'File':<40} {'Python':>10} {'Rust':>10} {'Speedup':>10} {'Status':>10}")
    print("-" * 85)

    failures = 0
    for file_path in test_files:
        name = file_path.name
        try:
            py_result, py_time = run_python(file_path)
        except RuntimeError as e:
            print(f"{name:<40} {RED}Python error{RESET}")
            print(f"  {e}")
            failures += 1
            continue

        try:
            rs_result, rs_time = run_rust(file_path)
        except RuntimeError as e:
            print(f"{name:<40} {'':>10} {RED}Rust error{RESET}")
            print(f"  {e}")
            failures += 1
            continue

        for key in SKIP_KEYS:
            py_result.pop(key, None)
            rs_result.pop(key, None)
        diffs = diff_json(py_result, rs_result)
        speedup = py_time / rs_time if rs_time > 0 else float("inf")

        if diffs:
            status = f"{RED}FAIL{RESET}"
            failures += 1
        else:
            status = f"{GREEN}PASS{RESET}"

        print(
            f"{name:<40} {py_time:>9.3f}s {rs_time:>9.3f}s {speedup:>9.1f}x {status:>20}"
        )

        if diffs:
            for d in diffs[:20]:
                print(d)
            if len(diffs) > 20:
                print(f"  ... and {len(diffs) - 20} more differences")

    print("-" * 85)
    total = len(test_files)
    passed = total - failures
    if failures:
        print(f"\n{RED}{BOLD}{failures}/{total} files FAILED{RESET}")
        sys.exit(1)
    else:
        print(f"\n{GREEN}{BOLD}{passed}/{total} files PASSED{RESET}")


if __name__ == "__main__":
    main()
