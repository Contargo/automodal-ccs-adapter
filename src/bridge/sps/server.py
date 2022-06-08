import time
from ctypes import Array, c_int8
from random import randint, uniform
from threading import Thread, Event
from typing import Dict, Union

from snap7.server import Server
from snap7.types import (
    wordlen_to_ctypes,
    S7WLByte,
    srvAreaPA,
    srvAreaMK,
    srvAreaPE,
    srvAreaDB,
)
from snap7.util import set_real, set_int, set_bool

from bridge.sps.data import db_items
from bridge.sps.types import spsint, spsreal, spsbool


class SpsServer:

    __dbs: dict[int, bytearray] = {}

    def __init__(self) -> None:
        self.shutdown_event = Event()
        self.server = Server()
        self.globaldata = (wordlen_to_ctypes[S7WLByte] * 10)()
        self.outputs = (wordlen_to_ctypes[S7WLByte] * 10)()
        self.inputs = (wordlen_to_ctypes[S7WLByte] * 10)()
        self.set_areas()
        self.generate_data()
        self.worker_thread: Thread = Thread(
            target=self.worker,
            args=(),
            name="sps worker",
            daemon=True,
        )
        self.worker_thread.start()
        
    def generate_data(self) -> None:
        for item in db_items:
            print(f"{item=}")
            if item.type is spsreal:
                set_real(
                    self.__dbs[item.dbnumber], item.start, round(uniform(0, 99), 2)
                )
            if item.type is spsint:
                set_int(self.__dbs[item.dbnumber], item.start, randint(0, 999))
            if item.type is spsbool:
                set_bool(
                    self.__dbs[item.dbnumber],
                    item.start,
                    item.bit_index,
                    bool(randint(0, 1)),
                )

    def set_areas(self) -> None:
        self.server.register_area(srvAreaPA, 0, self.outputs)
        self.server.register_area(srvAreaMK, 0, self.globaldata)
        self.server.register_area(srvAreaPE, 0, self.inputs)
        for item in db_items:
            if item.dbnumber not in self.__dbs.keys():
                sps_db = (wordlen_to_ctypes[S7WLByte] * 1000)()
                self.server.register_area(srvAreaDB, item.dbnumber, sps_db)
                self.__dbs[item.dbnumber] = sps_db

    def start(self) -> None:
        self.server.start()
        print("SPS_SERVER: is running")

    def worker(self) -> None:
        while not self.shutdown_event.is_set():
            event = self.server.pick_event()
            # if event:
            # print(f"SPS_SERVER: {self.server.event_text(event)}")
            time.sleep(0.01)

    def shutdown(self) -> None:
        print("SPS_SERVER: shutdown")
        self.shutdown_event.set()
        self.worker_thread.join()
        self.server.stop()
        self.server.destroy() # type: ignore[no-untyped-call]
