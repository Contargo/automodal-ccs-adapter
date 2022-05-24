import time
from collections import deque
from threading import Thread, Event, Lock
from typing import Deque, Optional

from snap7.client import Client
from snap7.types import Areas, S7AreaMK, S7AreaPA, S7AreaPE, S7AreaDB
from snap7.exceptions import Snap7Exception

from sps.client_data import SpsClientData


class SpsClient():
    def __init__(self, ip: str = "127.0.0.1") -> None:
        
        self.shutdown_event = Event()
        self.client = Client()
        self.queue: Deque = deque(maxlen=5)
        self.mqtt_queue: Optional[Deque] = None
        self.ip = ip
        self.connect()
        self.db1 = SpsClientData(Areas(S7AreaDB), dbnumber=1, client=self.client)
        self.define_data()
        self.worker: Thread = Thread(
            target=self.worker,
            args=(),
            name="sps worker",
            daemon=True,
        )
        self.worker.start()
        
    def define_data(self):
        self.db1.define_int(start=0, name="SomeInteger")
        self.db1.define_int(start=4, name="2Integer")
        self.db1.define_float(start=8, name="float1")
        
        
    def get_data(self) :
        self.db1.update()
        print(f"SPS_CLIENT db0 int: {self.db1.get_int('SomeInteger')}")
        print(f"SPS_CLIENT db0 float: {self.db1.get_float('float1')}")
        print(f"SPS_CLIENT db0 float as int: {self.db1.get_int('float1')}")
    
    def set_mqtt_queue(self, queue: deque):
        self.mqtt_queue: Deque = self.queue
        
    def connect(self):
        try:
            self.client.connect(self.ip, 0, 1)
        except Snap7Exception as exception:
            print(f"SPS_CLIENT: {exception}")
         
    def worker(self):
        while not self.shutdown_event.is_set():
            try:
                try:
                    data = self.queue.popleft()
                except IndexError as exception:
                    pass
                self.get_data()
                time.sleep(1)
            except Snap7Exception as exception:
                self.connect()
                time.sleep(1)
                #print(f"SPS_CLIENT: {exception}")

    def shutdown(self) -> None:
        print("SPS_CLIENT: shutdown")
        self.shutdown_event.set()
        self.worker.join()
        self.client.disconnect()
