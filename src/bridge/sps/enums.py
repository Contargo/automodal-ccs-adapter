from enum import StrEnum


class SPSStatus(StrEnum):
    INIT = "init"
    WAIT = "wait"
    RUNNING = "running"
    ERROR = "error"
    
