from random import random, randint, uniform
from threading import Thread, Event
from typing import List, Any, Dict

import time

from snap7.server import Server
from snap7.types import (
    wordlen_to_ctypes,
    S7WLByte,
    srvAreaPA,
    srvAreaMK,
    srvAreaPE,
    srvAreaDB,
)

from snap7.util import set_real, set_int, set_bool

from sps.data import db_items
from sps.types import spstypes, spsword, spsbyte, spsdint, spsint, spsreal, spsbool


class SpsServer:
    
    __dbs: Dict[int, any] = {}
    
    def __init__(self) -> None:
        self.shutdown_event = Event()
        self.server = Server()
        self.globaldata = (wordlen_to_ctypes[S7WLByte] * 10)()
        self.outputs = (wordlen_to_ctypes[S7WLByte] * 10)()
        self.inputs = (wordlen_to_ctypes[S7WLByte] * 10)()
        self.set_areas()
        self.generate_data()
        self.worker: Thread = Thread(
            target=self.worker,
            args=(),
            name="sps worker",
            daemon=True,
        )
        self.worker.start()

    def __random(self, type: spstypes):
        if type is spsreal:
            return round(uniform(0,99), 2)
        if type is spsbool:
            return bool(randint(0,1))
        return randint(0,999)

    def generate_data(self):
        for item in db_items:
            print(f"{item=}")
            if item.type is spsreal:
                set_real(self.__dbs[item.dbnumber], item.start, self.__random(item.type)) 
            if item.type is spsint:
                set_int(self.__dbs[item.dbnumber], item.start, self.__random(item.type)) 
            if item.type is spsbool:
                set_bool(self.__dbs[item.dbnumber], item.start, item.bit_index, item.self.__random(item.type)) 
                
    def set_areas(self):
        self.server.register_area(srvAreaPA, 0, self.outputs)
        self.server.register_area(srvAreaMK, 0, self.globaldata)
        self.server.register_area(srvAreaPE, 0, self.inputs)
        for item in db_items:
            if item.dbnumber not in self.__dbs.keys():
                db = (wordlen_to_ctypes[S7WLByte] * 1000)()
                self.server.register_area(srvAreaDB, item.dbnumber, db)
                self.__dbs[item.dbnumber] = db

    def start(self):
        self.server.start()
        print(f"SPS_SERVER: is running")

    def worker(self) -> None:
        while not self.shutdown_event.is_set():
            event = self.server.pick_event()
            #if event:
                #print(f"SPS_SERVER: {self.server.event_text(event)}")
            time.sleep(0.01)

    def shutdown(self) -> None:
        print("SPS_SERVER: shutdown")
        self.shutdown_event.set()
        self.worker.join()
        self.server.stop()
        self.server.destroy()
