import dataclasses
import json

from bridge.tams.types import CCSEvent, CCSFeature


def dataclass_to_json(datablass_object) -> str:  # type: ignore
    return datablass_object.to_json()


def generate_metadata(type_str: str) -> str:
    return dataclass_to_json(CCSEvent(type=f"net.contargo.logistics.tams.{type_str}"))


def generate_feature(feature_type: str) -> str:
    return dataclass_to_json(
        CCSFeature(
            type=feature_type,
        )
    )
