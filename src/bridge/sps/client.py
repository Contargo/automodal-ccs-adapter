import time
from collections import deque
from datetime import datetime, timedelta
from threading import Thread, Event, Lock
from typing import Deque, Optional, List

from snap7.client import Client
from snap7.exceptions import Snap7Exception
from snap7.types import Areas, S7AreaDB

from sps.client_data import SpsClientData
from sps.data import db_items
from sps.types import spstypes
from util.types import SpsQueueItem


class SpsClient:

    __db: List[SpsClientData] = []
    def __init__(self, ip: str = "127.0.0.1") -> None:

        self.shutdown_event = Event()
        self.client = Client()
        self.lock = Lock()
        self.ip = ip
        self.connect()
        self.db1 = SpsClientData(Areas(S7AreaDB), dbnumber=1, client=self.client)
        self.__db.append(self.db1)
        self.define_data()
        self.worker: Thread = Thread(
            target=self.worker,
            args=(),
            name="sps worker",
            daemon=True,
        )
        self.worker.start()

    def define_data(self):
        for item in db_items:
            for db in self.__db:
                if db.dbnumber == item.dbnumber:
                    db.define_data(name=item.name, start=item.start, type=item.type, bit_index=item.bit_index)

    def update_data(self):
        self.last_update_timestamp = datetime.now()
        for db in self.__db:
            with self.lock:
                db.update()
                
    def write_item(self, name: str, value: spstypes):
        for db in self.__db:
            if db.has_key(name):
                with self.lock:
                    db.write(name, value)  
                
    def read_value(self, name: str, type: type):
        for db in self.__db:
            if db.has_key(name):
                return db.read(name, type)

    def connect(self):
        try:
            self.client.connect(self.ip, 0, 1)
        except Snap7Exception as exception:
            print(f"SPS_CLIENT: {exception}")

    def worker(self):
        while not self.shutdown_event.is_set():
            try:
                self.update_data()
                time.sleep(1)
            except Snap7Exception as exception:
                self.connect()
                time.sleep(1)

    def shutdown(self) -> None:
        print("SPS_CLIENT: shutdown")
        self.shutdown_event.set()
        self.worker.join()
        self.client.disconnect()
