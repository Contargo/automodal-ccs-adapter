from dataclasses import dataclass
from typing import Union


@dataclass
class SPSClientQueueMSGsMeta:
    # in mm
    name: str
    topic: str

# binary
spsbool = bool
spsbyte = int  # 8bit
spsword = int  # 16bit

# numbers
spsint = int  # 16bit signed
spsdint = int  # 32bit signed

spsreal = float  # 32bit


spstypes = Union[spsbool, spsbyte, spsword, spsint, spsdint, spsreal]

@dataclass
class DBItem():
    dbnumber: int
    start: int
    name: str
    type: spstypes