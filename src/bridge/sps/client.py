import time
from collections import deque
from threading import Thread, Event, Lock
from typing import Deque, Optional

import snap7
from snap7.util import get_real, get_int
from snap7.types import Areas, S7AreaMK, S7AreaPA, S7AreaPE, S7AreaDB
from snap7.exceptions import Snap7Exception


class SpsClient():
    def __init__(self, ip: str = "127.0.0.1") -> None:
        
        self.shutdown_event = Event()
        self.client = snap7.client.Client()
        self.queue: Deque = deque(maxlen=5)
        self.mqtt_queue: Optional[Deque] = None
        self.ip = ip
        self.connect()
        self.worker: Thread = Thread(
            target=self.worker,
            args=(),
            name="sps worker",
            daemon=True,
        )
        self.worker.start()
        
    def get_data(self) :
        print(f"db1 string: {self.client.read_area(Areas(S7AreaDB) ,1,0,15)}")
        integer = self.client.read_area(Areas(S7AreaDB), dbnumber=0, start=0, size=4)
        print(f"db0 int: {get_int(integer,0)}")
    
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
                print(f"SPS_CLIENT: {exception}")

    def shutdown(self) -> None:
        print("SPS_CLIENT: shutdown")
        self.shutdown_event.set()
        self.worker.join()
        self.client.disconnect()
