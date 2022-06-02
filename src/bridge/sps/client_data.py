from typing import List, Type, Optional, Callable

from sps.types import spsint, spsdint, spsreal, spsbool, spsbyte, spsword, spstypes
from util.types import S7Area, DBNumber, SPSDataItem, Address, SpsQueueItem
from snap7.client import Client
from snap7.util import (
    get_real,
    get_int,
    get_bool,
    get_byte,
    get_word,
    get_dint,
    set_bool,
    set_byte,
    set_word,
    set_int,
    set_dint,
    set_real,
)


class SpsClientData:

    data: List[SPSDataItem] = []
    data_blocker: List[bool] = []

    def __init__(self, area: S7Area, dbnumber: DBNumber, client: Client) -> None:
        self.area = area
        self.dbnumber = dbnumber
        self.client = client

    def define_data(self, start: Address, name: str, type: type) -> None:
        self.data.append(
            SPSDataItem(
                s7Area=self.area,
                type=type,
                start=start,
                dbnumber=self.dbnumber,
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

    def __update_value(self, item: SPSDataItem, value: any):
        new_item = SPSDataItem(
            s7Area=item.s7Area,
            type=item.type,
            start=item.start,
            dbnumber=item.dbnumber,
            name=item.name,
            value=value,
            bit_index=item.bit_index,
        )
        return new_item

    def __read_from_sps(self, item: SPSDataItem, nr: int, size: int, func: Callable):
        data = self.client.read_area(
            item.s7Area, dbnumber=item.dbnumber, start=item.start, size=size
        )
        if item.type == spsbool:
            self.data[nr] = self.__update_value(item, func(data, 0, item.bit_index))
            return
        self.data[nr] = self.__update_value(item, func(data, 0))

    def __write_to_sps(self, item: SPSDataItem, size: int, func: Callable):
        data = bytearray(size)
        if item.type == spsbool:
            func(data, 0, item.bit_index, item.value)
        else:
            func(data, 0, 255)
        self.client.write_area(
            area=item.s7Area,
            dbnumber=item.dbnumber,
            start=item.start,
            size=size,
            data=data,
        )

    def update(self):
        for nr, item in enumerate(self.data):
            if item.type == spsbool:
                self.__read_from_sps(item, nr, 1, get_bool)
            if item.type == spsbyte:
                self.__read_from_sps(item, nr, 1, get_byte)
            if item.type == spsword:
                self.__read_from_sps(item, nr, 2, get_word)

            if item.type == spsint:
                self.__read_from_sps(item, nr, 2, get_int)
            if item.type == spsdint:
                self.__read_from_sps(item, nr, 4, get_dint)

            if item.type == spsreal:
                self.__read_from_sps(item, nr, 4, get_real)
            # print(f"read {item.type=} {item.value=}")

    def has_key(self, key: str):
        for data in self.data:
            if data.name == key:
                return True
        return False

    def write(self, name: str, value: spstypes):
        if self.has_key(name):
            new_item = self.__update_value(self.data[name], value)
            if new_item.type == spsbool:
                self.__write_to_sps(new_item, 1, set_bool)
            if new_item.type == spsbyte:
                self.__write_to_sps(new_item, 1, set_byte)
            if new_item.type == spsword:
                self.__write_to_sps(new_item, 2, set_word)

            if new_item.type == spsint:
                self.__write_to_sps(new_item, 2, set_int)
            if new_item.type == spsdint:
                self.__write_to_sps(new_item, 4, set_dint)

            if new_item.type == spsreal:
                self.__write_to_sps(new_item, 4, set_real)


    def read(self, name: str, type: type) -> spstypes:
        if self.has_key(name):
            return self.__get_data(name, type)
            
        