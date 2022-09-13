import time
from random import randint, uniform
from threading import Event, Thread

from snap7.server import Server
from snap7.types import (
    S7WLByte,
    srvAreaDB,
    srvAreaMK,
    srvAreaPA,
    srvAreaPE,
    wordlen_to_ctypes,
)
from snap7.util import (
    get_bool,
    get_byte,
    get_dint,
    get_int,
    set_bool,
    set_byte,
    set_dint,
    set_int,
    set_real,
)

from bridge.sps.data import db_items, get_item_with_name
from bridge.sps.types import spsbool, spsbyte, spsdint, spsint, spsreal


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
                set_dint(self.__dbs[item.dbnumber], item.start, randint(0, 200))

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

    def _set_bool(self, name: str, value: bool) -> None:
        item = get_item_with_name(name)
        # print(f"_set_bool: {item=}")
        set_bool(self.__dbs[item.dbnumber], item.start, item.bit_index, value)

    def _get_bool(self, name: str) -> bool:
        item = get_item_with_name(name)
        value = get_bool(self.__dbs[item.dbnumber], item.start, item.bit_index)
        # print(f"_get_bool: {value=} {item=}")
        return value

    def _set_int(self, name: str, value: int) -> None:
        item = get_item_with_name(name)
        # print(f"_set_int: {item=}")
        set_int(self.__dbs[item.dbnumber], item.start, value)

    def _get_byte(self, name: str) -> bytes:
        item = get_item_with_name(name)
        value = get_byte(self.__dbs[item.dbnumber], item.start)
        # print(f"_get_int: {value=} {item=}")
        return value

    def _set_byte(self, name: str, value: int) -> None:
        item = get_item_with_name(name)
        # print(f"_set_int: {item=}")
        set_byte(self.__dbs[item.dbnumber], item.start, value)

    def _get_int(self, name: str) -> int:
        item = get_item_with_name(name)
        value = get_int(self.__dbs[item.dbnumber], item.start)
        # print(f"_get_int: {value=} {item=}")
        return value

    def _set_dint(self, name: str, value: int) -> None:
        item = get_item_with_name(name)
        print(f"_set_dint: {item=}")
        set_dint(self.__dbs[item.dbnumber], item.start, value)

    def _get_dint(self, name: str) -> int:
        item = get_item_with_name(name)
        print(f"_get_int: {item=}")
        value = get_dint(self.__dbs[item.dbnumber], item.start)
        return value

    def set_defaults(self) -> None:
        self._set_bool("JobStatusDone", True)
        self._set_bool("JobStatusInProgress", False)
        self._set_bool("JobNewJob", False)

    def worker(self) -> None:

        self._set_bool("StatusPowerOn", True)
        self._set_bool("StatusManuelMode", False)
        self._set_bool("StatusAutomaticMode", True)
        self._set_bool("StatusWarning", False)
        self._set_bool("StatusError", False)
        self._set_byte("JobCommand", 0x00)
        self._set_bool("SandFusionStatus", True)

        while not self.shutdown_event.is_set():
            if self._get_bool("JobCancel"):  # cancel
                print(f"SERVER: cancel but have no active job")
                self._set_bool("JobCancel", False)
            if self._get_int("JobNewJob"):
                print(f"SERVER: new job")
                self._set_bool("JobStatusDone", False)
                self._set_bool("JobStatusInProgress", True)
                self._set_int("JobNewJob", 0)
                for _ in range(20):
                    self.shutdown_event.wait(0.5)
                    if self._get_bool("JobCancel"):  # cancel
                        self.shutdown_event.wait(2)
                        self._set_bool("JobCancel", False)
                        print(f"SERVER: cancel active job")
                        break
                self._set_bool("JobStatusDone", True)
                self._set_bool("JobStatusInProgress", False)
                self._set_dint("CraneCoordinatesZ", 1000)
                self._set_dint("CraneCoordinatesY", 1000)
                self._set_dint("CraneCoordinatesX", 1000)
            # event = self.server.pick_event()
            # if event:
            #   print(f"SPS_SERVER: {self.server.event_text(event)}")
            time.sleep(0.1)

    def shutdown(self) -> None:
        print("SPS_SERVER: shutdown")
        self.shutdown_event.set()
        self.worker_thread.join()
        self.server.stop()
        self.server.destroy()  # type: ignore[no-untyped-call]
