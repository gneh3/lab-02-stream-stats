from collections import Counter
from collections.abc import Iterator
from datetime import datetime

from .constants import TOP_ERROR_SOURCES_COUNT
from .models import EventLevel, LogEvent, Report, SkippedData


# analyze multiple files inside one class life cycle and then get report class
class LogsAnalyzer:
    def __init__(self, skip_data: SkippedData):
        self.events_count: int = 0
        self.counts_by_level: Counter[EventLevel] = Counter()
        self.counts_by_sources: Counter[str] = Counter()
        self.sources_by_error_counts: Counter[str] = Counter()
        self.min_time: datetime | None = None
        self.max_time: datetime | None = None
        self.top_n_errors : list[str] | None = None
        self.skip_data = skip_data


    def analyze_file(self, events_lazy : Iterator[LogEvent]) -> None:
        for event in events_lazy:
            self.events_count += 1
            self.counts_by_level[event.level] += 1
            self.counts_by_sources[event.source] += 1

            if event.level in (EventLevel.ERROR, EventLevel.CRITICAL):
                self.sources_by_error_counts[event.source] += 1

            if self.min_time is None or event.timestamp < self.min_time:
                self.min_time = event.timestamp
            if self.max_time is None or event.timestamp > self.max_time:
                self.max_time = event.timestamp

        sorted_sources = sorted(self.sources_by_error_counts.items(), key=lambda x: x[1], reverse=True)
        self.top_n_errors = [source for source, count in sorted_sources[:TOP_ERROR_SOURCES_COUNT]]

    def generate_relevant_report(self) -> Report:
        return Report(
            overall_events_count=self.events_count,
            leveled_events_count=dict(self.counts_by_level),
            source_events_count=dict(self.counts_by_sources),
            top_n_error_sources=self.top_n_errors,
            first_time_stamp=self.min_time if self.min_time else datetime.min,
            last_time_stamp=self.max_time if self.max_time else datetime.min,
            skipped_lines_count=self.skip_data.skipped_count)