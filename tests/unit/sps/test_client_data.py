from unittest.mock import MagicMock, patch

from pytest import fixture
from snap7.client import Client
from snap7.types import Areas, S7AreaDB

from bridge.sps.client_data import SpsClientData
from bridge.sps.types import spsbool, spsbyte, spsdint, spsint, spsreal, spsword


def client() -> Client:
    client = Client()
    client.write_area = MagicMock
    return client

@fixture
def data() -> SpsClientData:
    data = SpsClientData(Areas(S7AreaDB), dbnumber=1, client=client())
    data.define_data(start=0, name="test_int", data_type=spsint)
    #data.define_data(start=4, name="test_byte", data_type=spsbyte)
    #data.define_data(start=10, name="test_word", data_type=spsword)
    data.define_data(start=6, name="test_float", data_type=spsreal)
    data.define_data(start=14, name="test_dint", data_type=spsdint)
    data.define_data(start=18, name="test_bool", data_type=spsbool, bit_index=3)
    return data


def test_SpsClientData_read(
    data: SpsClientData,
) -> None:
    data.write(name="invalid_name", value=1337)
    assert data.get_int("invalid_name") is None
    data.write(name="test_int", value=1337)
    assert data.get_int("test_int") == 1337
    assert type(data.get_int("test_int")) == int
    
    data.write(name="test_float", value=1.1)
    assert data.get_real("test_float") == 1.1
    assert type(data.get_real("test_float")) == float
    
    #data.write(name="test_byte", value=256)
    #assert data.get_byte("test_byte") == 256
    #assert type(data.get_byte("test_byte")) == int
    #
    #data.write(name="test_word", value=1337)
    #assert data.get_word("test_word") == 1337
    #assert type(data.get_word("test_word")) == int
    
    data.write(name="test_dint", value=2135123155132132)
    assert data.get_dint("test_dint") == 2135123155132132
    assert type(data.get_dint("test_dint")) == int
    
    data.write(name="test_bool", value=False)
    assert data.get_bool("test_bool") == False
    assert type(data.get_bool("test_bool")) == bool
    
