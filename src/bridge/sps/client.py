import time
from collections import deque
from threading import Thread, Event, Lock
from typing import Deque

import snap7
from snap7.util import get_real, get_int
from snap7.types import Areas, S7AreaMK, S7AreaPA, S7AreaPE, S7AreaDB

class SpsClient():
    def __init__(self) -> None:
        
        self.shutdown_event = Event()
        
        self.client = snap7.client.Client()
        self.client.connect('127.0.0.1', 0, 1)
        self.queue: Deque = deque(maxlen=5)
        self.queue_lock = Lock()
        
        self.worker: Thread = Thread(
            target=self.worker,
            args=(),
            name="sps worker",
            daemon=True,
        )
        self.worker.start()
        
    def get_db1(self) :
        print(f"db1 string: {self.client.read_area(Areas(S7AreaDB) ,1,0,15)}")
        integer = self.client.read_area(Areas(S7AreaDB), dbnumber=0, start=0, size=4)
        print(f"db0 int: {get_int(integer,0)}")

    def push_data(self, data):
        with self.queue_lock:
            self.queue.append(data)

    def worker(self):
        while not self.shutdown_event.is_set():
            try:
                with self.queue_lock:
                    cods_box = self.queue.popleft()
            except IndexError as exception:
                pass
            self.get_db1()
            time.sleep(5)

    def shutdown(self) -> None:
        self.shutdown_event.set()
        self.worker.join()
