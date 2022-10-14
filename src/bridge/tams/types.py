import uuid
from dataclasses import dataclass, field
from datetime import datetime

from dataclasses_json import dataclass_json

from bridge.sps.types import spstypes
from bridge.tams.enums import CCSFeatureType, CCSJobType, CSSSiteType


def guid() -> str:
    return str(uuid.uuid4())


def timestamp() -> str:
    return datetime.now().isoformat()


@dataclass_json
@dataclass
class CCSEvent:
    # in mm
    type: str = "net.contargo.logistics.tams.TBD"
    site: str = CSSSiteType.TERMINAL
    timestamp: str = field(default_factory=timestamp)
    version: str = "v1"
    producer: str = "ccs.automodal.contargo.net"
    location: str = "DEKOB"
    eventId: str = field(default_factory=guid)


@dataclass_json
@dataclass
class CCSUnit:
    unitId: str = field(default_factory=guid)
    height: int = 0
    width: int = 0
    lenght: int = 0
    weight: int = 0
    type: str = "0000"
    number: str = "00000000000"
    piggy_back: bool = False


@dataclass_json
@dataclass
class CCSCoordinates:
    # in mm
    x: int = 1  # pylint: disable=invalid-name
    y: int = 2  # pylint: disable=invalid-name
    z: int = 3  # pylint: disable=invalid-name


@dataclass_json
@dataclass
class CCSJob:
    metadata: CCSEvent = field(default_factory=CCSEvent)
    type: str = CCSJobType.MOVE
    target: CCSCoordinates = field(default_factory=CCSCoordinates)
    unit: CCSUnit = field(default_factory=CCSUnit)


@dataclass_json
@dataclass
class CCSFeature:
    # in mm
    featureId: str = field(default_factory=guid)
    type: str = CCSFeatureType.FINAL_LANDING
    vendor: str = "GAGA Hühnerhof AG"
    version: str = "v1"


@dataclass_json
@dataclass
class CCSMetricEntry:
    name: str
    datatype: str
    value: spstypes


@dataclass_json
@dataclass
class CCSMetric:
    # in mm
    event: CCSEvent = field(default_factory=CCSEvent)
    metrics: list[CCSMetricEntry] = field(default_factory=list)


@dataclass_json
@dataclass
class CCSCraneDetails:
    # in mm
    event: CCSEvent = field(default_factory=CCSEvent)
    features: list[CCSFeature] = field(default_factory=list)
