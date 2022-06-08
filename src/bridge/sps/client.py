import time
from datetime import datetime
from threading import Thread, Event, Lock
from typing import List, Union, Optional

from snap7.client import Client
from snap7.exceptions import Snap7Exception
from snap7.types import Areas, S7AreaDB

from bridge.sps.client_data import SpsClientData
from bridge.sps.data import db_items
from bridge.sps.types import spstypes


class SpsClient:

    __db: list[SpsClientData] = []

    def __init__(self, ip_address: str = "127.0.0.1") -> None:
        self.last_update_timestamp = datetime.now()
        self.shutdown_event = Event()
        self.client = Client()
        self.lock = Lock()
        self.ip_address = ip_address
        self.connect()
        self.db1 = SpsClientData(Areas(S7AreaDB), dbnumber=1, client=self.client)
        self.__db.append(self.db1)
        self.define_data()
        self.worker_thread: Thread = Thread(
            target=self.worker,
            args=(),
            name="sps worker",
            daemon=True,
        )
        self.worker_thread.start()

    def define_data(self) -> None:
        for item in db_items:
            for sps_db in self.__db:
                if sps_db.dbnumber == item.dbnumber:
                    sps_db.define_data(
                        name=item.name,
                        start=item.start,
                        data_type=item.type,
                        bit_index=item.bit_index,
                    )

    def update_data(self) -> None:
        self.last_update_timestamp = datetime.now()
        for sps_db in self.__db:
            with self.lock:
                sps_db.update_from_sps()

    def write_item(self, name: str, value: spstypes) -> None:
        for sps_db in self.__db:
            if sps_db.has_key(name):
                with self.lock:
                    sps_db.write(name, value)

    def read_value(self, name: str, data_type: type) -> int | str | float | None:
        for sps_db in self.__db:
            if sps_db.has_key(name):
                return sps_db.read(name, data_type)
        return None

    def connect(self) -> None:
        try:
            self.client.connect(self.ip_address, 0, 1)
        except Snap7Exception as exception:
            print(f"SPS_CLIENT: {exception}")

    def worker(self) -> None:
        while not self.shutdown_event.is_set():
            try:
                self.update_data()
                time.sleep(1)
            except Snap7Exception as _:
                self.connect()
                time.sleep(1)

    def shutdown(self) -> None:
        print("SPS_CLIENT: shutdown")
        self.shutdown_event.set()
        self.worker_thread.join()
        self.client.disconnect()
