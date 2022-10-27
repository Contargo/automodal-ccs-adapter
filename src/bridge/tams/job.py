from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, NamedTuple, Optional, Type

from dataclasses_json import dataclass_json
from marshmallow import ValidationError
from snap7.types import Areas

from bridge.sps.enums import SPSStatus
from bridge.tams.enums import CCSJobStatus, CCSJobType
from bridge.tams.helper import dataclass_to_json
from bridge.tams.types import CCSEvent, CCSJob, CCSUnit
from bridge.util.types import Address, DBNumber


def timestamp() -> str:
    return datetime.now().isoformat()


class TamsJob(NamedTuple):
    name: str
    s7Area: Areas
    dbnumber: DBNumber
    start: Address
    type: type[CCSJobType]
    value: Any


@dataclass_json
@dataclass
class _JobState:
    jobType: str = CCSJobType.MOVE  # pylint: disable=invalid-name
    jobStatus: str = CCSJobStatus.DONE  # pylint: disable=invalid-name
    unit: CCSUnit = field(default_factory=CCSUnit)
    created: str = field(default_factory=timestamp)
    metadata: CCSEvent = field(default_factory=CCSEvent)


class CCSJobState:
    __running_job: CCSJob | None = None
    __job_status: str = CCSJobStatus.DONE
    __job_created: str = ""

    def __init__(self) -> None:
        pass

    def has_job(self) -> bool:
        return self.__running_job is not None

    def get_job(self) -> CCSJob | None:
        return self.__running_job

    def get_job_as_json(self) -> str:
        return dataclass_to_json(self.__running_job)

    def set_new_job(self, job_json: str) -> str:
        try:
            # pylint: disable=no-member
            job = CCSJob.from_json(job_json)  # type: ignore
        except ValidationError:
            return "invalid"
        if not self.has_job():
            self.__running_job = job
            self.__job_created = datetime.now().isoformat()
            return "OK"
        return "has job"

    def job_done(self) -> None:
        print("[JOB][job_done] called")
        self.__running_job = None

    def get_state_as_json(self) -> str:
        if self.__running_job:
            return dataclass_to_json(
                _JobState(
                    created=self.__job_created,
                    unit=self.__running_job.unit,
                    jobStatus=self.__job_status,
                    jobType=self.__running_job.type,
                )
            )
        return dataclass_to_json(
            _JobState(
                created=self.__job_created,
                jobStatus=self.__job_status,
            )
        )
