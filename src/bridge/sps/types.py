from dataclasses import dataclass
from typing import TypeVar, Union


@dataclass
class SPSClientQueueMSGsMeta:
    # in mm
    name: str
    topic: str


spsbool = bool


class spsbyte(bytes):
    pass


class spsword(bytes):
    pass


class spsint(int):
    pass


class spsdint(int):
    pass


class spsreal(float):
    pass


spstypes = Union[  # pylint: disable=invalid-name
    spsbool, spsbyte, spsword, spsint, spsdint, spsreal
]

spstypevar = TypeVar("spstypevar", bound=spstypes)


@dataclass(frozen=True)
class DBItem:
    dbnumber: int
    start: int
    name: str
    type: type  # spstypes
    bit_index: int = 0
