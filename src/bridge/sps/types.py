from dataclasses import dataclass
from typing import Union, TypeVar


@dataclass
class SPSClientQueueMSGsMeta:
    # in mm
    name: str
    topic: str


# binary
spsbool = bool  # pylint: disable=invalid-name
spsbyte = int  # 8bit # pylint: disable=invalid-name
spsword = int  # 16bit # pylint: disable=invalid-name

# numbers
spsint = int  # 16bit signed # pylint: disable=invalid-name
spsdint = int  # 32bit signed # pylint: disable=invalid-name

spsreal = float  # 32bit # pylint: disable=invalid-name


spstypes = Union[  # pylint: disable=invalid-name
    spsbool, spsbyte, spsword, spsint, spsdint, spsreal
]

spstypevar = TypeVar("spstypevar", bound=spstypes)


@dataclass
class DBItem:
    dbnumber: int
    start: int
    name: str
    type: type  # spstypes
    bit_index: int = 0
