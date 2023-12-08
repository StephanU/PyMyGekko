"""Test for vents in MyGekko software version 680016"""
import pytest
from aiohttp import ClientSession
from aiohttp import web
from PyMyGekko import MyGekkoApiClientBase
from PyMyGekko.resources.vents import VentBypassMode
from PyMyGekko.resources.vents import VentBypassState
from PyMyGekko.resources.vents import VentCoolingMode
from PyMyGekko.resources.vents import VentDehumidMode
from PyMyGekko.resources.vents import VentDeviceModel
from PyMyGekko.resources.vents import VentElementInfo
from PyMyGekko.resources.vents import VentFeature
from PyMyGekko.resources.vents import VentSubWorkingMode
from PyMyGekko.resources.vents import VentWorkingLevel
from PyMyGekko.resources.vents import VentWorkingMode


async def var_response(_request):
    """mocked MyGekko resources response"""
    var_response_file = open(
        "tests/vents/data/api_var_response_680016.json", encoding="UTF-8"
    )
    return web.Response(status=200, body=var_response_file.read())


async def var_status_response(_request):
    """mocked MyGekko status response"""
    status_response_file = open(
        "tests/vents/data/api_var_status_response_680016.json", encoding="UTF-8"
    )
    return web.Response(status=200, body=status_response_file.read())


@pytest.fixture
def mock_server(aiohttp_server):
    """mock server"""
    app = web.Application()
    app.router.add_get("/api/v1/var", var_response)
    app.router.add_get("/api/v1/var/status", var_status_response)
    return aiohttp_server(app)


@pytest.mark.asyncio
async def test_get_vents(mock_server):
    """test for the vents"""
    server = await mock_server
    async with ClientSession() as session:
        api = MyGekkoApiClientBase(
            {},
            session,
            scheme=server.scheme,
            host=server.host,
            port=server.port,
        )

        await api.read_data()
        vents = api.get_vents()

        assert vents is not None
        assert len(vents) == 1

        assert vents[0].entity_id == "item0"
        assert vents[0].name == "Wohnraumlüftung"
        assert vents[0].device_model == VentDeviceModel.PLUGGIT
        assert vents[0].element_info == VentElementInfo.OK
        assert vents[0].air_quality is None
        assert vents[0].co2 == 764.0
        assert vents[0].exhaust_air_temperature == 23.05
        assert vents[0].exhaust_air_working_level == 25.0
        assert vents[0].outgoing_air_temperature == 11.48
        assert vents[0].outside_air_temperature == 8.02
        assert vents[0].relative_humidity == 46.0
        assert vents[0].supply_air_temperature == 21.13
        assert vents[0].supply_air_working_level == 25.0
        assert vents[0].cooling_mode == VentCoolingMode.OFF
        assert vents[0].dehumid_mode == VentDehumidMode.OFF
        assert vents[0].bypass_mode == VentBypassMode.AUTO
        assert vents[0].bypass_state == VentBypassState.AUTO
        assert vents[0].working_level == VentWorkingLevel.LEVEL_1
        assert vents[0].working_mode == VentWorkingMode.MANUAL
        assert vents[0].sub_working_mode == VentSubWorkingMode.EXHAUST_SUPPLY
        assert len(vents[0].supported_features) == 3
        assert VentFeature.CO2 in vents[0].supported_features
        assert VentFeature.HUMIDITY in vents[0].supported_features
        assert VentFeature.WORKING_LEVEL in vents[0].supported_features
