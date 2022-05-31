from enum import StrEnum, Enum

from sps.types import SPSClientQueueMSGsMeta


class SPSStatus(StrEnum):
    INIT = "init"
    WAIT = "wait"
    RUNNING = "running"
    ERROR = "error"


class SPSClientQueueMSGs(Enum):
    KATZ_POSITION = SPSClientQueueMSGsMeta(
        name="katz_position",
        topic="position/katz"
    )
    CRANE_POSITION = SPSClientQueueMSGsMeta(
        name="crane_position",
        topic="position/crane"
    )
    SPREADER_POSITION = SPSClientQueueMSGsMeta(
        name="spreader_position",
        topic="position/spreader"
    )
    