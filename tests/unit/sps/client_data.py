from unittest.mock import MagicMock

from pytest import fixture
from pytest_mock import MockerFixture
from snap7.types import Areas, S7AreaDB

from sps.client_data import SpsClientData

@fixture
def data() -> SpsClientData:
    data = SpsClientData(Areas(S7AreaDB), dbnumber=1, client=MagicMock)
    data.define_int(start=0, name="test_int1")
    data.define_int(start=4, name="test_int2")
    data.define_float(start=8, name="test_float")
    return data



def test_SpsClientData_read(
    data: data,
) -> None:
    data.get_int("test_int")
