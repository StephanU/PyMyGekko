import pytest
from aiohttp import ClientSession
from aiohttp import web
from PyMyGekko import MyGekkoApiClient
from PyMyGekko.resources.HotWaterSystems import HotWaterSystemFeature
from PyMyGekko.resources.HotWaterSystems import HotWaterSystemState


async def var_response(request):
    varResponseFile = open("tests/hotwater_systems/data/api_var_response_680016.json")
    return web.Response(status=200, body=varResponseFile.read())


async def var_status_response(request):
    statusResponseFile = open(
        "tests/hotwater_systems/data/api_var_status_response_680016.json"
    )
    return web.Response(status=200, body=statusResponseFile.read())


@pytest.fixture
def mock_server(aiohttp_server):
    app = web.Application()
    app.router.add_get("/api/v1/var", var_response)
    app.router.add_get("/api/v1/var/status", var_status_response)
    return aiohttp_server(app)


@pytest.mark.asyncio
async def test_get_hotwater_systems(mock_server):
    server = await mock_server
    async with ClientSession() as session:
        api = MyGekkoApiClient(
            "USERNAME",
            "APIKEY",
            "GEKKOID",
            session,
            scheme=server.scheme,
            host=server.host,
            port=server.port,
        )

        await api.read_data()
        hotWaterSystems = api.get_hot_water_systems()

        assert hotWaterSystems is not None
        assert len(hotWaterSystems) == 1

        assert hotWaterSystems[0].id == "item0"
        assert hotWaterSystems[0].name == "Warmwasserspeicher"
        assert hotWaterSystems[0].state == HotWaterSystemState.ON
        assert hotWaterSystems[0].target_temperature == 55.0
        assert hotWaterSystems[0].current_temperature_bottom == 22.0
        assert hotWaterSystems[0].current_temperature_top == 61.1
        assert len(hotWaterSystems[0].supported_features) == 2
        assert HotWaterSystemFeature.ON_OFF in hotWaterSystems[0].supported_features
        assert (
            HotWaterSystemFeature.TARGET_TEMPERATURE
            in hotWaterSystems[0].supported_features
        )
