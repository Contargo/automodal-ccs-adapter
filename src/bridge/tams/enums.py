from enum import Enum

from strenum import StrEnum

seaport = "seaport"  # pylint: disable=invalid-name


class CSSSiteType(StrEnum):
    TERMINAL = "terminal"
    SEAPORT = "seaport"


class CCSJobType(StrEnum):
    MOVE = "move"
    PICK = "pick"
    DROP = "drop"
    PARK = "park"
    REMOTE = "remote"
    STORMPIN = "stormPin"
    CANCEL = "cancel"


class CCSJobStatus(StrEnum):
    INPROGRESS = "inProgress"
    WEIGHTED = "weighted"
    CONTINUED = "continued"
    STOPPED = "stopped"
    REJECTED = "rejected"
    PAUSED = "paused"
    DONE = "done"


class CCSFeatureType(StrEnum):
    CIS = "cis"
    FINAL_LANDING = "finallanding"


class SpsJobType(Enum):
    PICK = 0x01
    DROP = 0x02
    PARK = 0x04
    REMOTE = 0x08
    STORM_PIN = 0x10
