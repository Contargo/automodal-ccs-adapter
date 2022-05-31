from threading import Thread, Event

import snap7
import time

from snap7.types import (
    wordlen_to_ctypes,
    S7WLByte,
    srvAreaPA,
    srvAreaMK,
    srvAreaPE,
    srvAreaDB,
)


class SpsServer:
    def __init__(self) -> None:
        self.shutdown_event = Event()
        self.server = snap7.server.Server()
        self.globaldata = (wordlen_to_ctypes[S7WLByte] * 10)()
        self.outputs = (wordlen_to_ctypes[S7WLByte] * 10)()
        self.inputs = (wordlen_to_ctypes[S7WLByte] * 10)()
        self.db0 = (wordlen_to_ctypes[S7WLByte] * 100)()
        self.db1 = (wordlen_to_ctypes[S7WLByte] * 100)()
        self.set_areas()
        self.generate_data()
        self.worker: Thread = Thread(
            target=self.worker,
            args=(),
            name="sps worker",
            daemon=True,
        )
        self.worker.start()

    def generate_data(self):
        snap7.util.set_real(self.db1, 8, 1.234)  # srvAreaPA
        snap7.util.set_int(self.db1, 0, 42)
        snap7.util.set_int(self.db1, 0, 12313)

    def set_areas(self):
        self.server.register_area(srvAreaPA, 0, self.outputs)
        self.server.register_area(srvAreaMK, 0, self.globaldata)
        self.server.register_area(srvAreaPE, 0, self.inputs)
        self.server.register_area(srvAreaDB, 0, self.db0)
        self.server.register_area(srvAreaDB, 1, self.db1)

    def start(self):
        self.server.start()
        print(f"SPS_SERVER: is running")

    def worker(self) -> None:
        while not self.shutdown_event.is_set():
            event = self.server.pick_event()
            if event:
                print(f"SPS_SERVER: {self.server.event_text(event)}")
            time.sleep(0.01)

    def shutdown(self) -> None:
        print("SPS_SERVER: shutdown")
        self.shutdown_event.set()
        self.worker.join()
        self.server.stop()
        self.server.destroy()
