import dataclasses
import json
import uuid
from datetime import datetime

from ccs.enums import CCSFeatureType
from ccs.types import CCSEvent, CCSFeature


def dataclass_to_json(object: dataclasses.dataclass):
    return json.dumps(dataclasses.asdict(object))


def generate_metadata(type: str):
    return dataclass_to_json(CCSEvent(type=f"net.contargo.logistics.tams.{type}"))


def generate_feature(type: CCSFeatureType):
    return dataclass_to_json(
        CCSFeature(
            type=type,
        )
    )
