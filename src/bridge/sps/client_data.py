from typing import List, Type, Optional

from util.types import S7Area, DBNumber, SPSDataItem, Address
from snap7.client import Client
from snap7.util import get_real, get_int

class SpsClientData():
    
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
                value=0
            )
        )
        
    def define_float(self, start: Address,name: str) -> None:
        self.data.append(
            SPSDataItem(
                s7Area=self.area,
                type=float,
                start=start,
                dbnumber=self.db,
                name=name,
                value=0
            )
        )
        
    def get_int(self, name: str) -> Optional[SPSDataItem]:
        for item in self.data:
            if item.name == name and item.type == int:
                return item.value
        return None
    
    def get_float(self, name: str) -> Optional[SPSDataItem]:
        for item in self.data:
            if item.name == name and item.type == float:
                return item.value
        return None
    
    def update_value(self, item: SPSDataItem, value: any):
        new_item = SPSDataItem(
                s7Area=item.s7Area,
                type=item.type,
                start=item.start,
                dbnumber=item.dbnumber,
                name=item.name,
                value=value
            )
        return new_item
    
    def update(self):
        for nr, item in enumerate(self.data):
            if item.type == int:
                data = self.client.read_area(item.s7Area, dbnumber=item.dbnumber, start=item.start, size=4)
                self.data[nr] = self.update_value(item, get_int(data,0))
                
            if item.type == float:
                data = self.client.read_area(item.s7Area, dbnumber=item.dbnumber, start=item.start, size=4)
                self.data[nr] = self.update_value(item, get_real(data,0))
            #print(f"read {item.type=} {item.value=}")