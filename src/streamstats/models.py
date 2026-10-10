from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class EventLevel(StrEnum):
    DEBUG = "Debug"
    INFO = "Info"
    WARNING = "Warning"
    ERROR = "Error"
    CRITICAL = "Critical"

@dataclass
class LogEvent:
    timestamp: datetime
    level: EventLevel
    source: str
    message: str


@dataclass 
class Report:
    leveled_events_count: dict[EventLevel, int]
    source_events_count: dict[str, int]
    overall_events_count: int = 0
    skipped_lines_count: int = 0
    top_n_error_sources: list[str] | None = None
    first_time_stamp: datetime | None = None
    last_time_stamp: datetime | None = None

@dataclass
class SkippedData:
    get_to_skip_invalid: bool
    skipped_count: int = 0

