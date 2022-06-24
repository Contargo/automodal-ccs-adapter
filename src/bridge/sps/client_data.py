import inspect
from functools import partial
from typing import List, Optional, Callable, Type, Any

from snap7.client import Client
from snap7.exceptions import Snap7Exception
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
from .types import (
    spsint,
    spsdint,
    spsreal,
    spsbool,
    spsbyte,
    spsword,
    spstypevar,
    spstypes,
)


class SpsClientData:
    def __init__(self, area: Areas, dbnumber: DBNumber, client: Client) -> None:
        self.raw_data: bytearray | None = None
        self.data: list[SPSDataItem[spstypes]] = []
        self.data_blocker: list[bool] = []
        self.area = area
        self.dbnumber = dbnumber
        self.client = client
        self.size = 0
        
    def _get_type_size(self, data_type: Type[spstypevar]):
        if data_type in [spsword, spsint]:
            return  2
        if data_type in [spsdint, spsreal]:
            return  4
        return  1

    def define_data(
        self, start: Address, name: str, data_type: Type[spstypevar], bit_index: int = 0
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
        type_size = self._get_type_size(data_type)
        if self.size < start + type_size:
            self.size = start + type_size

    def __get_data(self, name: str, data_type: Type[spstypevar]) -> spstypevar | None:
        for item in self.data:
            if item.name == name:
                if item.type == data_type and (isinstance(item.value, data_type) or issubclass(data_type, type(item.value))):
                    return item.value
                else:
                    print(f"__get_data found name but type error: {self.dbnumber}, {name=}, {type(item.value)=}, {item.value}, {data_type=}, {item.type=}, "
                          f"{item.type == data_type=}, "
                          f"{isinstance(item.value, data_type)=}, "
                          f"{issubclass(data_type, type(item.value))=}, ")
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

    def __read_from_sps(self):
        try:
            self.raw_data = self.client.read_area(
                self.area, dbnumber=self.dbnumber, start=0, size=self.size
            )
        except Snap7Exception as _:
            pass
        except TypeError as error:
            print(error)

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
        try:
            self.client.write_area(
                area=self.area,
                dbnumber=self.dbnumber,
                start=item.start,
                data=data,
            )
        except Snap7Exception as _:
            print("YOUR STUPID!!!")
            pass

    def update_from_sps(self) -> None:
        self.__read_from_sps()
        for number, item in enumerate(self.data):
            if item.type == spsbool:
                self.data[number].value = get_bool(
                    self.raw_data, item.start, bool_index=item.bit_index
                )
            if item.type == spsbyte:
                byte_data = get_byte(self.raw_data, item.start)
                if type(byte_data) == int:
                    byte_data = byte_data.to_bytes(1, byteorder="little") # type: ignore
                self.data[number].value = byte_data
            if item.type == spsword:
                byte_data = get_word(self.raw_data, item.start)
                if type(byte_data) == int:
                    byte_data = byte_data.to_bytes(2, byteorder="little") # type: ignore
                self.data[number].value = byte_data
            if item.type == spsint:
                self.data[number].value = get_int(self.raw_data, item.start)
            if item.type == spsdint:
                self.data[number].value = get_dint(self.raw_data, item.start)
            if item.type == spsreal:
                self.data[number].value = get_real(self.raw_data, item.start)

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
        func: Callable[[bytearray, int, spstypevar], Any],
    ) -> None:
        func(
            self.raw_data,
            item.start,
            item.value,
        )
        data = bytearray(self._get_type_size(item.type))
        func(
            data,
            0,
            item.value,
        )
        self.client.db_write(
            db_number=item.dbnumber,
            start=item.start,
            data=data,
        )

    def write(self, name: str, value: spstypevar) -> None:
        data = self.get_data_by_name(name)
        if data:
            data.value = value
            if data.type == spsbool:
                raise ValueError(
                    "no boolean write is allowed! Use Byte representation."
                )
            if data.type == spsbyte:
                self.__write_to_sps(data, set_byte)
            if data.type == spsword:
                self.__write_to_sps(data, set_word)
            if data.type == spsint:
                self.__write_to_sps(data, set_int)  # type: ignore[arg-type]
            if data.type == spsdint:
                self.__write_to_sps(data, set_dint)  # type: ignore[arg-type]
            if data.type == spsreal:
                self.__write_to_sps(data, set_real)
            return
        print("NO DATA")

    def read(self, name: str, data_type: Type[spstypevar]) -> spstypevar | None:
        if self.has_key(name):
            return self.__get_data(name, data_type)
        return None
