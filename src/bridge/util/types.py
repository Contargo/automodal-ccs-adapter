from typing import NamedTuple, Union, List


class Position(NamedTuple):
    x: float
    y: float

class SpsQueueItem(NamedTuple):
    name: str
    data: Union[bool, int]

Collision = bool

MQTT_Topic = str
MQTT_Payload = Union[List[str], str]