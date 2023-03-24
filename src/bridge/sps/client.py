from __future__ import annotations
import time
from datetime import datetime
from threading import Event, Lock, Thread
from typing import List, Optional, Type, Union, Any

from snap7.client import Client
from snap7.exceptions import Snap7Exception
from snap7.types import Areas, S7AreaDB

from bridge.sps.client_data import SpsClientData
from bridge.sps.data import db_items
from bridge.sps.types import spstypes


class SpsClient:

    __db: dict[int, SpsClientData] = {}

    def __init__(self, ip_address: str = "127.0.0.1", verbose: bool = False) -> None:
        self.verbose = verbose
        self.last_update_timestamp = datetime.now()
        self.shutdown_event = Event()
        self.client = Client()
        self.lock = Lock()
        self.ip_address = ip_address
        self.define_areas()
        self.define_data()
        self.worker_thread: Thread = Thread(
            target=self.worker,
            args=(),
            name="sps worker",
            daemon=True,
        )

    def start(self) -> None:
        self.worker_thread.start()

    def define_areas(self) -> None:
        for item in db_items:
            if item.dbnumber not in self.__db.keys():
                db = SpsClientData(
                    Areas(S7AreaDB), dbnumber=item.dbnumber, client=self.client
                )
                self.__db[item.dbnumber] = db
                print(
                    f"[SPS_CLIENT][define_area] {self.__db[item.dbnumber]=}, {self.__db[item.dbnumber].dbnumber=}"
                )

    def define_data(self) -> None:
        for item in db_items:
            if self.verbose:
                print(
                    f"[SPS_CLIENT][define_data] {item=}, {self.__db[item.dbnumber].dbnumber}"
                )
            self.__db[item.dbnumber].define_data(
                name=item.name,
                start=item.start,
                data_type=item.type,
                bit_index=item.bit_index,
            )

    def update_data(self) -> None:
        self.last_update_timestamp = datetime.now()
        for db_nr in self.__db:
            with self.lock:
                self.__db[db_nr].update_from_sps()

    def write_item(self, name: str, value: spstypes) -> None:
        for db_nr in self.__db:
            if self.__db[db_nr].has_key(name):
                with self.lock:
                    print(f"[SPS_CLIENT][write_item] {db_nr=} {name=} {value=}")
                    self.__db[db_nr].write(name, value)

    def read_value(self, name: str, data_type: Type[spstypes]) -> spstypes:
        for db_nr in self.__db:
            if self.__db[db_nr].has_key(name):
                return self.__db[db_nr].read(name, data_type)
        raise ValueError("name not in __db")

    def get_table(self) -> list[Any]:
        data = []
        for item in db_items:
            value = self.read_value(item.name, item.type)
            data.append([item.name, item.dbnumber, item.start, item.type, value])
        return data

    def connect(self) -> None:
        try:
            print(f"[SPS_CLIENT][connect] ip_address {self.ip_address}")
            if self.ip_address == "127.0.0.1":
                print("[SPS_CLIENT][connect] is localhost")
                self.client.connect(self.ip_address, 0, 1)
            else:
                self.client.connect(self.ip_address, 0, 0)
        except Snap7Exception as exception:
            print(f"[SPS_CLIENT][connect] {exception}")
        except RuntimeError as _:
            print("[SPS_CLIENT][connect] RuntimeError")

    def worker(self) -> None:
        while not self.shutdown_event.is_set():
            try:
                # print("update data")
                self.update_data()
                time.sleep(1)
            except Snap7Exception as _:
                print("[SPS_CLIENT][worker] Snap7Exception")
                self.connect()
                time.sleep(1)
            except RuntimeError as _:
                print("[SPS_CLIENT][worker] RuntimeError")
                self.connect()
                time.sleep(1)

    def shutdown(self) -> None:
        print("[SPS_CLIENT][shutdown]  shutdown")
        self.shutdown_event.set()
        self.worker_thread.join()
        self.client.disconnect()
