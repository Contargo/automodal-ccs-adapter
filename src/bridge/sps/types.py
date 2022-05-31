from dataclasses import dataclass


@dataclass
class SPSClientQueueMSGsMeta:
    # in mm
    name: str
    topic: str