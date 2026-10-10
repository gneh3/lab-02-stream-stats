import os
import subprocess
import sys
from pathlib import Path

import pytest

from streamstats.analysis import LogsAnalyzer
from streamstats.errors import StreamStatsError
from streamstats.models import EventLevel, SkippedData
from streamstats.parsers import parse_csv, parse_jsonl

DIR = Path(__file__).parent

def test_jsonl_parsing():
    path = DIR/"valid_logs.jsonl"
    skip_data = SkippedData(get_to_skip_invalid=False)
    events = list(parse_jsonl(path, skip_data))

    assert len(events) == 8
    assert events[0].level == EventLevel.INFO
    assert events[0].source == "auth"
    assert events[5].message == "no memory lol"


def test_csv_parsing():
    path = DIR/"valid_logs.csv"
    skip_data = SkippedData(get_to_skip_invalid=False)
    events = list(parse_csv(path, skip_data))

    assert events[0].level == EventLevel.INFO
    assert events[0].source == "auth"
    assert events[5].message == "no memory lol"


def test_broken_logs_raise_error():
    path = DIR/"broken_logs.jsonl"
    skip_data = SkippedData(get_to_skip_invalid=False)

    with pytest.raises(StreamStatsError):
        list(parse_jsonl(path, skip_data))


def test_broken_logs_skipped_with_flag():
    path = DIR/"broken_logs.jsonl"
    skip_data = SkippedData(get_to_skip_invalid=True)
    events = list(parse_jsonl(path, skip_data))
    assert skip_data.skipped_count == 3
    assert events


def test_unicode_support():
    path = DIR/"unicode.jsonl"
    skip_data = SkippedData(get_to_skip_invalid=False)
    events = list(parse_jsonl(path, skip_data))

    assert events[0].source == "источнек"
    assert events[0].message == "нельзя"


def test_empty_file():
    path = DIR/"empty.jsonl"
    if path.exists():
        skip_data = SkippedData(get_to_skip_invalid=False)
        events = list(parse_jsonl(path, skip_data))
        assert len(events) == 0

        analyzer = LogsAnalyzer(skip_data)
        analyzer.analyze_file(iter(events))
        report = analyzer.generate_relevant_report()
        assert report.overall_events_count == 0

def test_multiple_files_aggregation():
    jsonl_path_1 = DIR/"valid_logs.jsonl"
    jsonl_path_2 = DIR/"valid_logs2.jsonl"

    skip_data = SkippedData(get_to_skip_invalid=False)
    analyzer = LogsAnalyzer(skip_data)

    events = parse_jsonl(jsonl_path_1, skip_data)
    analyzer.analyze_file(events)
    events = parse_jsonl(jsonl_path_2, skip_data)
    analyzer.analyze_file(events)
    report = analyzer.generate_relevant_report()

    assert report.overall_events_count == 16
    assert report.leveled_events_count[EventLevel.ERROR] == 4


def test_cli_integration_real():
    input_file = DIR / "valid_logs.jsonl"
    output_report = DIR / "test_report.json"

    if input_file.exists():
        env = os.environ.copy()
        project_root = DIR.parent
        env["PYTHONPATH"] = str(project_root / "src")
        result = subprocess.run(
            [
                sys.executable, "-m", "streamstats",
                "analyze", str(input_file),
                "--format", "jsonl",
                "--output", str(output_report)
            ],
            env=env,
            check=False,
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert output_report.exists()

        if output_report.exists():
            output_report.unlink()