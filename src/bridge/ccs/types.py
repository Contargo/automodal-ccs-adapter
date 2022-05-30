import uuid
from dataclasses import dataclass, field
from datetime import datetime

from dataclasses_json import dataclass_json

from ccs.enums import CCSJobType, CCSJobStatus, CSSSiteType, CCSFeatureType

def GUID():
    return str(uuid.uuid4())

def timestamp():
    return datetime.now().isoformat()

@dataclass_json
@dataclass
class CCSEvent():
    # in mm
    type: str = "net.contargo.logistics.tams.TBD"
    site: CSSSiteType = CSSSiteType.TERMINAL
    timestamp: str = field(default_factory=timestamp)
    version: str = "v1"
    producer: str = "ccs.automodal.contargo.net"
    location: str = "DEKOB"
    GUID: str = field(default_factory=GUID)

    
@dataclass_json
@dataclass
class CCSUnit():  
    unitId: str = field(default_factory=GUID)
    height: int = 100
    width: int = 200
    lenght: int = 300
    weight: int = 999
    type: str = "20GP"
    number: str = "CSQU3054383"
    piggyBack: bool = False

@dataclass_json
@dataclass
class CCSCoordinates():
    # in mm
    x: int = 1
    y: int = 2
    z: int = 3

@dataclass_json
@dataclass
class CCSJob():
    metadata: CCSEvent = field(default_factory=CCSEvent)
    type: CCSJobType = CCSJobType.MOVE
    target: CCSCoordinates = field(default_factory=CCSCoordinates)
    unit: CCSUnit = field(default_factory=CCSUnit)
    
@dataclass_json
@dataclass
class CCSFeature():
    # in mm
    featureId: str = field(default_factory=GUID)
    type: CCSFeatureType  = CCSFeatureType.FINAL_LANDING
    vendor: str = "GAGA Hühnerhof AG"
    version: str = "v1"
