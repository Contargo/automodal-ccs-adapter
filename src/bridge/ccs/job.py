from datetime import datetime
from enum import Enum
from marshmallow import ValidationError
from typing import NamedTuple, Type, Any, Optional

from ccs.enums import CCSJobType, CCSJobStatus
from ccs.helper import dataclass_to_json
from ccs.types import CCSJob, CCSUnit, CCSEvent
from sps.enums import SPSStatus
from util.types import S7Area, DBNumber, Address

from dataclasses_json import dataclass_json
from dataclasses import dataclass, field


def timestamp():
    return


class TamsJob(NamedTuple):
    name: str
    s7Area: S7Area
    dbnumber: DBNumber
    start: Address
    type: Type
    value: Any


@dataclass_json
@dataclass
class _JobState:
    jobType: CCSJobType = CCSJobType.MOVE
    jobStatus: CCSJobStatus = CCSJobStatus.DONE
    unit: CCSUnit = field(default_factory=CCSUnit)
    created: str = field(default_factory=timestamp)
    metadata: CCSEvent = field(default_factory=CCSEvent)


class CCSJobState:
    __running_job: Optional[CCSJob] = None
    __sps_status: SPSStatus = SPSStatus.INIT
    __job_status: CCSJobStatus = CCSJobStatus.DONE
    __job_created: str = ""

    def __init__(self) -> None:
        pass

    def has_job(self) -> bool:
        return self.__running_job is not None

    def sps_status(self) -> SPSStatus:
        return self.__sps_status

    def get_job_as_json(self):
        return dataclass_to_json(self.__running_job)

    def set_new_job(self, job_json: str) -> str:
        try:
            job = CCSJob.from_json(job_json)
        except ValidationError:
            return "invalid"
        if not self.has_job():
            self.__running_job = job
            self.__job_created = datetime.now().isoformat()
            self.__job_status = CCSJobStatus.INPROGRESS
            return "OK"
        return "has job"

    def get_state_as_json(self):
        return dataclass_to_json(
            _JobState(
                created=self.__job_created,
                unit=self.__running_job.unit,
                jobStatus=self.__job_status,
                jobType=self.__running_job.type,
            )
        )
