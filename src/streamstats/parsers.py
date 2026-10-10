import csv
import json
import logging
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path

from .constants import *
from .errors import *
from .models import EventLevel, LogEvent, SkippedData

logger = logging.getLogger(__name__)

def verif_and_create_event(data: dict, file_name: str, string_num: int) -> LogEvent:
    # if any of them is uninitialize
    if any(not (i in data) for i in (TIMESTAMP, LEVEL, SOURCE, MESSAGE)):
        raise StreamStatsError(StreamStatsErrorType.UNSUPPORTED_FORMAT_EXCEPTION,
                               f"Invalid {next(i for i in (TIMESTAMP, LEVEL, SOURCE, MESSAGE) if not (i in data))}, line: {string_num} in {file_name}")
    # if source is empty
    elif data[SOURCE] == "":
        raise StreamStatsError(StreamStatsErrorType.UNSUPPORTED_FORMAT_EXCEPTION, f"source is empty, line {string_num} in {file_name}")

    # if invalid time
    try:
        timestamp = datetime.fromisoformat(str(data[TIMESTAMP]))
    except (ValueError, TypeError) as exception:
        raise StreamStatsError(
            StreamStatsErrorType.INVALID_TIMESTAMP_EXCEPTION,
            f"{data.get(TIMESTAMP)}, line {string_num} in {file_name}") from exception
    # our exception based on value/type error

    try:
        level = EventLevel(data[LEVEL])
    except ValueError as exception:
        raise StreamStatsError(
            StreamStatsErrorType.INVALID_EVENT_EXCEPTION,
            f"invalid log level: {data.get(LEVEL)}, line {string_num} in {file_name}"
        ) from exception

    return LogEvent(
        timestamp=timestamp,
        level=level,
        source=data[SOURCE],
        message=data[MESSAGE])

def parse_jsonl(path: Path, skip_data: SkippedData) -> Iterator[LogEvent]:
    with open(path, "r", encoding="utf-8") as f:
        # enumerating num of str and str, del spaces, skip empty, try parse to json and check if we stop when error
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if line == "":
                continue
            try:
                data = json.loads(line)
                event = verif_and_create_event(data, path.name, line_num)
                # dynamic expression handlers
                yield event
            except StreamStatsError as exception:
                if not skip_data.get_to_skip_invalid:
                    raise
                logger.warning(f"skipped invalid line: {exception}")
                skip_data.skipped_count += 1


def parse_csv(path: Path, skip_data: SkippedData) -> Iterator[LogEvent]:
    with open(path, "r", encoding="utf-8") as f:
        # parsing to dict using first string as a keys
        reader = csv.DictReader(f)

        # starting from 2, 1st string is the names-string
        # row is dict with keys from 1st string and values from current
        for line_num, row in enumerate(reader, start=2):
            try:
                event = verif_and_create_event(row, path.name, line_num)
                yield event
            except StreamStatsError as exception:
                if not skip_data.get_to_skip_invalid:
                    raise
                logger.warning(f"skipped invalid line: {exception}")
                skip_data.skipped_count += 1
