from builtins import function
from typing import List, Type, Optional

from sps.types import spsint, spsdint, spsreal, spsbool, spsbyte, spsword
from util.types import S7Area, DBNumber, SPSDataItem, Address
from snap7.client import Client
from snap7.util import get_real, get_int, get_bool, get_byte, get_word, get_dint


class SpsClientData:

    data: List[SPSDataItem] = []
    data_blocker: List[bool] = []

    def __init__(self, area: S7Area, dbnumber: DBNumber, client: Client) -> None:
        self.area = area
        self.db = dbnumber
        self.client = client

    def define_int(self, start: Address, name: str) -> None:
        self.data.append(
            SPSDataItem(
                s7Area=self.area,
                type=int,
                start=start,
                dbnumber=self.db,
                name=name,
                value=0,
            )
        )

    def define_float(self, start: Address, name: str) -> None:
        self.data.append(
            SPSDataItem(
                s7Area=self.area,
                type=float,
                start=start,
                dbnumber=self.db,
                name=name,
                value=0,
            )
        )
        
    def __get_data(self, name: str, type: type):
        for item in self.data:
            if item.name == name and item.type == type:
                return item.value
        return None
    
    def get_bool(self, name: str) -> Optional[SPSDataItem]:
        return self.__get_data(name, spsbool)
    
    def get_byte(self, name: str) -> Optional[SPSDataItem]:
        return self.__get_data(name, spsbyte)
    
    def get_word(self, name: str) -> Optional[SPSDataItem]:
        return self.__get_data(name, spsword)
    
    def get_int(self, name: str) -> Optional[SPSDataItem]:
        return self.__get_data(name, spsint)
    
    def get_dint(self, name: str) -> Optional[SPSDataItem]:
        return self.__get_data(name, spsdint)

    def get_real(self, name: str) -> Optional[SPSDataItem]:
        return self.__get_data(name, spsreal)
    
    
    

    def update_value(self, item: SPSDataItem, value: any):
        new_item = SPSDataItem(
            s7Area=item.s7Area,
            type=item.type,
            start=item.start,
            dbnumber=item.dbnumber,
            name=item.name,
            value=value,
            bit_index=item.bit_index
        )
        return new_item
    
    def __update(self, item: SPSDataItem, nr: int, size: int, func: function):
        data = self.client.read_area(
            item.s7Area, dbnumber=item.dbnumber, start=item.start, size=size
        )
        if item.type == spsbool:
            self.data[nr] = self.update_value(item, func(data, 0, item.bit_index))
            return
        self.data[nr] = self.update_value(item, func(data, 0))
        
    def update(self):
        for nr, item in enumerate(self.data):
            if item.type == spsbool:
                self.__update(item, nr, 1, get_bool)
            if item.type == spsbyte:
                self.__update(item, nr, 1, get_byte)
            if item.type == spsword:
                self.__update(item, nr, 2, get_word)
                
                
            if item.type == spsint:
                self.__update(item, nr, 2, get_int)
            if item.type == spsdint:
                self.__update(item, nr, 4, get_dint)
                
            if item.type == spsreal:
                self.__update(item, nr, 4, get_real)
            # print(f"read {item.type=} {item.value=}")
