import time
from collections import deque
from threading import Thread, Event, Lock
from typing import Deque, Optional, List

from snap7.client import Client
from snap7.types import Areas, S7AreaMK, S7AreaPA, S7AreaPE, S7AreaDB
from snap7.exceptions import Snap7Exception

from sps.client_data import SpsClientData
from sps.data import db_items
from sps.types import spsint, spsreal, spstypes
from util.types import SpsQueueItem


class SpsClient:

    __db: List[SpsClientData] = []

    def __init__(self, ip: str = "127.0.0.1") -> None:

        self.shutdown_event = Event()
        self.client = Client()
        self.queue: Deque = deque(maxlen=5)
        self.mqtt_client_queue: Optional[Deque] = None
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
                    db.define_data(name=item.name, start=item.start, type=item.type)

    def get_data(self):
        # todo: slow down update?
        for db in self.__db:
            db.update()
        print(f"SPS_CLIENT db0 int: {self.db1.get_int('SomeInteger')}")
        print(f"SPS_CLIENT db0 float: {self.db1.get_real('float1')}")
        print(f"SPS_CLIENT db0 float as int: {self.db1.get_int('float1')}")

    def write_queue_item(self, data: SpsQueueItem):
        for db in self.__db:
            if db.has_key(data.name):
                db.write(data.name, data.data)
                
    def write_item(self, name: str, value: spstypes):
        for db in self.__db:
            if db.has_key(name):
                db.write(name, value)  
                
    def read_value(self, name: str, type: type):
        for db in self.__db:
            if db.has_key(name):
                return db.read(name, type)

    def set_mqtt_queue(self, queue: deque):
        self.mqtt_client_queue: Deque = queue

    def connect(self):
        try:
            self.client.connect(self.ip, 0, 1)
        except Snap7Exception as exception:
            print(f"SPS_CLIENT: {exception}")

    def worker(self):
        while not self.shutdown_event.is_set():
            try:
                try:
                    data: SpsQueueItem = self.mqtt_client_queue.popleft()
                    self.write_queue_item(data)
                except IndexError as exception:
                    pass
                self.get_data()
                time.sleep(0.1)
            except Snap7Exception as exception:
                self.connect()
                time.sleep(1)

    def shutdown(self) -> None:
        print("SPS_CLIENT: shutdown")
        self.shutdown_event.set()
        self.worker.join()
        self.client.disconnect()
