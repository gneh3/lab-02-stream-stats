import argparse
import sys
from pathlib import Path

from .analysis import LogsAnalyzer
from .errors import StreamStatsError
from .models import SkippedData
from .parsers import parse_csv, parse_jsonl
from .report import save_report_to_json


def main() -> None:
    parser = argparse.ArgumentParser(
        description="streamstats - stream log analyzer (csv / jsonl)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze_parser = subparsers.add_parser(
        "analyze",
        help="analyze logs, generate json report")
    analyze_parser.add_argument(
        "inputs",
        nargs="+", # for multiple args
        type=Path,
        help="paths to one or more input log files")
    analyze_parser.add_argument(
        "--format",
        choices=["csv", "jsonl"],
        required=True,
        help="input files format")
    analyze_parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="path to the resulting json report")
    analyze_parser.add_argument(
        "--skip-invalid",
        action="store_true", # will give us bool
        help="skip invalid lines and log warnings instead of throwing an error")

    args = parser.parse_args()

    if args.command == "analyze":
        skip_data = SkippedData(get_to_skip_invalid=args.skip_invalid, skipped_count=0)
        analyzer = LogsAnalyzer(skip_data=skip_data)

        try:
            for file_path in args.inputs:
                if not file_path.exists():
                    print(f"error: file not found: {file_path}", file=sys.stderr)
                    sys.exit(2)

                if args.format == "jsonl":
                    events = parse_jsonl(file_path, skip_data)
                else:
                    events = parse_csv(file_path, skip_data)

                analyzer.analyze_file(events)

            report = analyzer.generate_relevant_report()
            save_report_to_json(report, args.output)

        except StreamStatsError as exception:
            print(f"error: {exception}", file=sys.stderr)
            sys.exit(2)
        except Exception as exception: # noqa: BLE001
            print(f"unexpected error: {exception}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()