from typing import Optional

from bridge.sps.types import DBItem, spsint, spsreal, spsbool, spsbyte, spsdint

db_items = [
    DBItem(dbnumber=4, start=8, name="WegLandseite", type=spsdint),
    DBItem(dbnumber=4, start=12, name="WegWasserSeite", type=spsdint),
    DBItem(dbnumber=4, start=18, name="WegKatze", type=spsdint),
    DBItem(dbnumber=2500, start=0, name="TriggerwordRecv", type=spsint),
    DBItem(dbnumber=2500, start=2, name="WatchdogRecv", type=spsbool, bit_index=0),
    DBItem(dbnumber=2500, start=4, name="JobCoordinatesZ", type=spsdint),
    DBItem(dbnumber=2500, start=8, name="JobCoordinatesX", type=spsdint),
    DBItem(dbnumber=2500, start=12, name="JobCoordinatesY", type=spsdint),
    DBItem(dbnumber=2500, start=16, name="JobBay", type=spsint),
    DBItem(dbnumber=2500, start=18, name="JobRow", type=spsint),
    DBItem(dbnumber=2500, start=20, name="JobTier", type=spsint),
    DBItem(dbnumber=2500, start=22, name="JobBayType", type=spsint),
    DBItem(dbnumber=2500, start=24, name="JobSpreaderSize", type=spsint),
    DBItem(dbnumber=2500, start=26, name="JobNewJob", type=spsint),
    DBItem(dbnumber=2500, start=28, name="JobType", type=spsbyte),
    DBItem(dbnumber=2500, start=28, name="JobPick", type=spsbool, bit_index=0),
    DBItem(dbnumber=2500, start=28, name="JobDrop", type=spsbool, bit_index=1),
    DBItem(dbnumber=2500, start=28, name="JobPark", type=spsbool, bit_index=2),
    DBItem(dbnumber=2500, start=28, name="JobRemote", type=spsbool, bit_index=3),
    DBItem(dbnumber=2500, start=28, name="JobStormPin", type=spsbool, bit_index=4),
    DBItem(dbnumber=2500, start=30, name="SandStatus", type=spsbyte),
    DBItem(dbnumber=2500, start=30, name="SandFusionStatus", type=spsbool, bit_index=0),
    DBItem(dbnumber=2501, start=0, name="TriggerwordSend", type=spsint),
    DBItem(dbnumber=2501, start=2, name="WatchdogSend", type=spsbool, bit_index=0),
    DBItem(dbnumber=2501, start=4, name="CraneCoordinatesZ", type=spsdint),
    DBItem(dbnumber=2501, start=8, name="CraneCoordinatesX", type=spsdint),
    DBItem(dbnumber=2501, start=12, name="CraneCoordinatesY", type=spsdint),
    DBItem(dbnumber=2501, start=16, name="Weight", type=spsreal),
    DBItem(dbnumber=2501, start=20, name="Status", type=spsbyte),
    DBItem(dbnumber=2501, start=20, name="StatusPowerOn", type=spsbool, bit_index=0),
    DBItem(dbnumber=2501, start=20, name="StatusManuelMode", type=spsbool, bit_index=1),
    DBItem(
        dbnumber=2501, start=20, name="StatusAutomaticMode", type=spsbool, bit_index=2
    ),
    DBItem(dbnumber=2501, start=20, name="StatusWarning", type=spsbool, bit_index=3),
    DBItem(dbnumber=2501, start=20, name="StatusError", type=spsbool, bit_index=4),
    DBItem(
        dbnumber=2501, start=20, name="StatusWindWarning", type=spsbool, bit_index=5
    ),
    DBItem(dbnumber=2501, start=20, name="StatusWindError", type=spsbool, bit_index=6),
    DBItem(dbnumber=2501, start=24, name="SpreaderLanded", type=spsbool, bit_index=0),
    DBItem(
        dbnumber=2501, start=24, name="SpreaderNotLanded", type=spsbool, bit_index=1
    ),
    DBItem(dbnumber=2501, start=24, name="SpreaderError", type=spsbool, bit_index=2),
    DBItem(dbnumber=2501, start=26, name="SpreaderPosition", type=spsint),
    # JobType Output missing DB 2501, start 28
    DBItem(dbnumber=2501, start=30, name="JobStatus", type=spsbyte),
    DBItem(
        dbnumber=2501, start=30, name="JobStatusInProgress", type=spsbool, bit_index=0
    ),
    DBItem(
        dbnumber=2501, start=30, name="JobStatusWeighted", type=spsbool, bit_index=1
    ),
    DBItem(
        dbnumber=2501, start=30, name="JobStatusContinued", type=spsbool, bit_index=2
    ),
    DBItem(dbnumber=2501, start=30, name="JobStatusStopped", type=spsbool, bit_index=3),
    DBItem(
        dbnumber=2501, start=30, name="JobStatusRejected", type=spsbool, bit_index=4
    ),
    DBItem(dbnumber=2501, start=30, name="JobStatusPaused", type=spsbool, bit_index=5),
    DBItem(dbnumber=2501, start=30, name="JobStatusDone", type=spsbool, bit_index=6),
]


def get_item_with_name(name: str) -> DBItem | None:
    for item in db_items:
        if item.name == name:
            return item
    print(f"DB_ITEM: item not found {name=}")
    return None
