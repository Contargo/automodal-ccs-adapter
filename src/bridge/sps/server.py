from threading import Thread, Event

import snap7
import time


class SpsServer():
    def __init__(self) -> None:
        self.shutdown_event = Event()
        self.server = snap7.server.Server()
        self.server.start()
        self.worker: Thread = Thread(
            target=self.worker,
            args=(),
            name="sps worker",
            daemon=True,
        )
        self.worker.start()
        print(f"SERVER: is running")
        
    def generate_data(self):
        size = 100
        data = (snap7.types.wordlen_to_ctypes[snap7.types.S7WLByte] * size)()
        for index in range(size):
            data[index] = index
        self.server.register_area(snap7.types.srvAreaDB, 1, data)
        
        
    def worker(self) -> None:
        while not self.shutdown_event.is_set():
            event = self.server.pick_event()
            if event:
                print(f"SERVER: {self.server.event_text(event)}")
            time.sleep(.01)
        

    def shutdown(self) -> None:
        self.shutdown_event.set()
        self.worker.join()
        self.server.stop()
        self.server.destroy()
