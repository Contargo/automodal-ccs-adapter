from enum import Enum
from marshmallow import ValidationError
from typing import NamedTuple, Type, Any, Optional

from ccs.helper import dataclass_to_json
from ccs.types import CCSJob
from sps.enums import SPSStatus
from util.types import S7Area, DBNumber, Address

class TamsJob(NamedTuple):
    name: str
    s7Area: S7Area
    dbnumber: DBNumber
    start: Address
    type: Type
    value: Any
    
    
class CCSJobState():
    __running_job: Optional[CCSJob] = None
    __sps_status: SPSStatus = SPSStatus.INIT
    
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
            return "OK"
        return "has job"