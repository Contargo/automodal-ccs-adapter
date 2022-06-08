from functools import partial
from typing import List, Optional, Callable, Type, Any

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

from snap7.types import Areas
from bridge.util.types import DBNumber, SPSDataItem, Address
from .types import spsint, spsdint, spsreal, spsbool, spsbyte, spsword, spstypevar, spstypes


class SpsClientData:

    data: list[SPSDataItem[spstypes]] = []
    data_blocker: list[bool] = []

    def __init__(self, area: Areas, dbnumber: DBNumber, client: Client) -> None:
        self.area = area
        self.dbnumber = dbnumber
        self.client = client

    def define_data(
        self, start: Address, name: str, data_type: type, bit_index: int = 0
    ) -> None:
        self.data.append(
            SPSDataItem(
                s7Area=self.area,
                type=data_type,
                start=start,
                dbnumber=self.dbnumber,
                name=name,
                value=True,
                bit_index=bit_index,
            )
        )

    def __get_data(self, name: str, data_type: type[spstypevar]) -> spstypevar | None:
        for item in self.data:
            if item.name == name and item.type == data_type and isinstance(item.value, data_type):
                return item.value
        return None

    def get_bool(self, name: str) -> bool | None:
        return self.__get_data(name, spsbool)

    def get_byte(self, name: str) -> int | None:
        return self.__get_data(name, spsbyte)

    def get_word(self, name: str) -> int | None:
        return self.__get_data(name, spsword) 

    def get_int(self, name: str) -> int | None:
        return self.__get_data(name, spsint)

    def get_dint(self, name: str) -> int | None:
        return self.__get_data(name, spsdint)

    def get_real(self, name: str) -> float | None:
        return self.__get_data(name, spsreal)

    def __read_from_sps(
        self,
        item: SPSDataItem[spstypevar],
        number: int,
        size: int,
        func: Callable[[bytearray, int], spstypevar],
    ) -> None:
        data = self.client.read_area(
            item.s7Area, dbnumber=item.dbnumber, start=item.start, size=size
        )
        self.data[number].value = func(data, 0)


    def __write_bool_to_sps(
        self,
        item: SPSDataItem[spstypevar],
        size: int,
    ) -> None:
        assert isinstance(item.value, spsbool)
        data = bytearray(size)
        set_bool(
            data,
            0,
            item.bit_index,
            item.value,
        )
        self.client.write_area(
            area=item.s7Area,
            dbnumber=item.dbnumber,
            start=item.start,
            data=data,
        )

    def update_from_sps(self) -> None:
        for number, item in enumerate(self.data):
            if item.type == spsbool:
                self.__read_from_sps(item, number, 1, partial(get_bool, bit_index=item.bit_index))
            #if item.type == spsbyte:
            #    self.__read_from_sps(item, number, 1, get_byte)
            #if item.type == spsword:
            #    self.__read_from_sps(item, number, 2, get_word)

            if item.type == spsint:
                self.__read_from_sps(item, number, 2, get_int)
            if item.type == spsdint:
                self.__read_from_sps(item, number, 4, get_dint)

            if item.type == spsreal:
                self.__read_from_sps(item, number, 4, get_real)
            # print(f"read {item.type=} {item.value=}")

    def has_key(self, key: str) -> bool:
        for data in self.data:
            if data.name == key:
                return True
        return False

    def get_data_by_name(self, name: str) -> SPSDataItem[spstypes] | None:
        for data in self.data:
            if data.name == name:
                return data
        return None

    def __write_to_sps(
        self,
        item: SPSDataItem[spstypevar],
        size: int,
        func: Callable[[bytearray, int, spstypevar], Any],
    ) -> None:
        data = bytearray(size)
        func(
            data,
            0,
            item.value,
        )
        self.client.write_area(
            area=item.s7Area,
            dbnumber=item.dbnumber,
            start=item.start,
            data=data,
        )
        
    def write(self, name: str, value: spstypevar) -> None:
        data = self.get_data_by_name(name)
        if data:
            data.value = value
            if data.type == spsbool:
                self.__write_bool_to_sps(data, 1)
            #if data.type == spsbyte:
            #    self.__write_to_sps(data, 1, set_byte)
            #if data.type == spsword:
            #    self.__write_to_sps(data, 2, set_word)

            if data.type == spsint:
                self.__write_to_sps(data, 2, set_int) # type: ignore[arg-type]
            if data.type == spsdint:
                self.__write_to_sps(data, 4, set_dint) # type: ignore[arg-type]

            if data.type == spsreal:
                self.__write_to_sps(data, 4, set_real)

    def read(self, name: str, data_type: type) -> spstypevar | None:
        if self.has_key(name):
            return self.__get_data(name, data_type)
        return None
