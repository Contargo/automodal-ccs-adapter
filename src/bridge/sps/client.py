import time
from threading import Thread, Event

import snap7

class SpsClient():
    def __init__(self) -> None:
        
        self.shutdown_event = Event()
        
        self.client = snap7.client.Client()
        self.client.connect('localhost', 0, 3)
        
        
        self.worker: Thread = Thread(
            target=self.worker,
            args=(),
            name="sps worker",
            daemon=True,
        )
        self.worker.start()
        
    def get_db1(self) :
        all_data = self.client.db_get(1)
        print(all_data)

    def worker(self):
        while not self.shutdown_event.is_set():
            self.get_db1()
            time.sleep(5)

    def shutdown(self) -> None:
        self.shutdown_event.set()
        self.worker.join()
