from enum import StrEnum


class StreamStatsErrorType(StrEnum):
    UNSUPPORTED_FORMAT_EXCEPTION = "unsupported format exception"
    INVALID_EVENT_EXCEPTION = "invalid event exception"
    INVALID_TIMESTAMP_EXCEPTION = "invalid timestamp exception"
    CLI_CONFIG_EXCEPTION = "cli config exception"

class StreamStatsError(Exception):
    def __init__(self, error_type: StreamStatsErrorType, details: str = ""):
        self.error_type = error_type
        message = error_type.value
        if details != "":
            message = f"{message}, {details})"
        # from error subtype and message calls base Exception constructor
        super().__init__(message)

