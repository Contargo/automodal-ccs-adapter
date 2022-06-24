import time
from random import randint, uniform
from threading import Thread, Event

from snap7.server import Server
from snap7.types import (
    wordlen_to_ctypes,
    S7WLByte,
    srvAreaPA,
    srvAreaMK,
    srvAreaPE,
    srvAreaDB,
)
from snap7.util import set_real, set_int, set_bool, set_dint, get_bool, get_int, set_byte

from bridge.sps.data import db_items, get_item_with_name
from bridge.sps.types import spsint, spsreal, spsbool, spsdint, spsbyte


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
        self.set_defaults()
        self.worker_thread: Thread = Thread(
            target=self.worker,
            args=(),
            name="sps worker",
            daemon=True,
        )
        self.worker_thread.start()

    def generate_data(self) -> None:
        for item in db_items:
            print(f"SERVER: {item=}")
            if item.type is spsreal:
                set_real(
                    self.__dbs[item.dbnumber], item.start, round(uniform(0, 99), 2)
                )
            if item.type is spsbyte:
                set_byte(self.__dbs[item.dbnumber], item.start, 255)
            if item.type is spsint:
                set_int(self.__dbs[item.dbnumber], item.start, randint(0, 999))
            if item.type is spsdint:
                set_dint(self.__dbs[item.dbnumber], item.start, randint(0, 999))

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
        # print("SPS_SERVER: is running")
        self.server.start()

    def _set_bool(self, name: str, value: bool):
        item = get_item_with_name(name)
        # print(f"_set_bool: {item=}")
        set_bool(self.__dbs[item.dbnumber], item.start, item.bit_index, value)

    def _get_bool(self, name: str):
        item = get_item_with_name(name)
        value = get_bool(self.__dbs[item.dbnumber], item.start, item.bit_index)
        # print(f"_get_bool: {value=} {item=}")
        return value

    def _set_int(self, name: str, value: bool):
        item = get_item_with_name(name)
        # print(f"_set_int: {item=}")
        set_int(self.__dbs[item.dbnumber], item.start, value)

    def _get_int(self, name: str):
        item = get_item_with_name(name)
        value = get_int(self.__dbs[item.dbnumber], item.start)
        #print(f"_get_int: {value=} {item=}")
        return value

    def set_defaults(self):
        self._set_bool("JobStatusDone", True)
        self._set_bool("JobStatusInProgress", False)
        self._set_bool("JobNewJob", False)

    def worker(self) -> None:
        while not self.shutdown_event.is_set():
            if self._get_int("JobNewJob"):
                self._set_bool("JobStatusDone", False)
                self._set_bool("JobStatusInProgress", True)
                self._set_int("JobNewJob", False)
                self.shutdown_event.wait(10)
                self._set_bool("JobStatusDone", True)
                self._set_bool("JobStatusInProgress", False)
            #event = self.server.pick_event()
            #if event:
            #   print(f"SPS_SERVER: {self.server.event_text(event)}")
            time.sleep(0.1)

    def shutdown(self) -> None:
        print("SPS_SERVER: shutdown")
        self.shutdown_event.set()
        self.worker_thread.join()
        self.server.stop()
        self.server.destroy()  # type: ignore[no-untyped-call]
