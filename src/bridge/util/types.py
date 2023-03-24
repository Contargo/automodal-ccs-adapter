from dataclasses import dataclass
from typing import Generic, List, NamedTuple, Optional, Type, Union

from snap7.types import Areas

from bridge.sps.types import SPSClientQueueMSGsMeta, spstypes, spstypevar

DBNumber = int
Address = int


@dataclass
class SPSDataItem(Generic[spstypevar]):
    name: str
    s7Area: Areas
    dbnumber: DBNumber
    start: Address
    type: Type[spstypevar]
    value: spstypevar
    bit_index: int = 0


class Position(NamedTuple):
    x: float
    y: float


class SpsQueueItem(NamedTuple):
    name: str
    data: spstypes


class MqttQueueItem(NamedTuple):
    name: str
    meta: SPSClientQueueMSGsMeta
    data: bool 


Collision = bool

MQTT_Topic = str  # pylint: disable=invalid-name
MQTT_Payload = Union[List[str], str]  # pylint: disable=invalid-name
