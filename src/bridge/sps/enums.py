from enum import StrEnum, Enum

from sps.types import SPSClientQueueMSGsMeta


class SPSStatus(StrEnum):
    INIT = "init"
    WAIT = "wait"
    RUNNING = "running"
    ERROR = "error"


class SPSClientQueueMSGs(Enum):
    KATZ_POSITION = SPSClientQueueMSGsMeta(name="katz_position", topic="katz_position")
    CRANE_POSITION = SPSClientQueueMSGsMeta(
        name="crane_position", topic="crane_position"
    )
    SPREADER_POSITION = SPSClientQueueMSGsMeta(
        name="spreader_position", topic="spreader_position"
    )
