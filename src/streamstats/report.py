import json
from datetime import datetime
from pathlib import Path

from .models import EventLevel, Report


def save_report_to_json(report: Report, output_path: Path) -> None:
    report_dict = {
        "overall_events_count": report.overall_events_count,
        "skipped_lines_count": report.skipped_lines_count,
        # enums to strs
        "leveled_events_count": {str(level.value if isinstance(level, EventLevel) else None): count
                                  for level, count in report.leveled_events_count.items()},
        "source_events_count": report.source_events_count,
        "top_n_error_sources": report.top_n_error_sources if report.top_n_error_sources is not None else [],
        # datetime to ISO
        "first_time_stamp": report.first_time_stamp.isoformat() if report.first_time_stamp and report.first_time_stamp != datetime.min else None,
        "last_time_stamp": report.last_time_stamp.isoformat() if report.last_time_stamp and report.last_time_stamp != datetime.min else None,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        # indent = 4 to make it readable and ensure_ascii to КИРИЛЛИЦА
        json.dump(report_dict, f, ensure_ascii=False, indent=4)