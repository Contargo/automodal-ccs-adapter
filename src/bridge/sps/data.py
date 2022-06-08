from typing import Optional

from bridge.sps.types import DBItem, spsint, spsreal, spsbool, spsbyte

db_items = [
    DBItem(dbnumber=1, start=0, name="SomeInteger", type=spsint),
    DBItem(dbnumber=1, start=4, name="2Integer", type=spsint),
    DBItem(dbnumber=1, start=8, name="float1", type=spsreal),
    DBItem(dbnumber=2, start=0, name="collision_status", type=spsbool, bit_index=0),
    DBItem(dbnumber=3, start=0, name="katz_position", type=spsreal),
    DBItem(dbnumber=3, start=4, name="crane_position", type=spsreal),
    DBItem(dbnumber=3, start=8, name="spreader_position", type=spsreal),
    DBItem(dbnumber=4, start=0, name="job_status", type=spsbyte),
    DBItem(dbnumber=4, start=1, name="job_type", type=spsbyte),
    DBItem(dbnumber=4, start=2, name="job_target_x", type=spsreal),
    DBItem(dbnumber=4, start=6, name="job_target_y", type=spsreal),
    DBItem(dbnumber=4, start=10, name="job_target_z", type=spsreal),
    DBItem(dbnumber=4, start=14, name="container_size", type=spsint),
]


def get_item_with_name(name: str) -> DBItem | None:
    for item in db_items:
        if item.name == name:
            return item
    print(f"DB_ITEM: item not found {name=}")
    return None
