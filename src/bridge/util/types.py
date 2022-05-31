from typing import NamedTuple, Union, List, Type, Any

from snap7.types import Areas

from sps.enums import SPSClientQueueMSGs
from sps.types import SPSClientQueueMSGsMeta

S7Area = Areas
DBNumber = int
Address = int


class SPSDataItem(NamedTuple):
    name: str
    s7Area: S7Area
    dbnumber: DBNumber
    start: Address
    type: Type
    value: Any


class Position(NamedTuple):
    x: float
    y: float


class SpsQueueItem(NamedTuple):
    name: str
    data: Union[bool, int]

class MqttQueueItem(NamedTuple):
    name: str
    meta: SPSClientQueueMSGsMeta
    data: Union[bool, int, Position]

Collision = bool

MQTT_Topic = str
MQTT_Payload = Union[List[str], str]
