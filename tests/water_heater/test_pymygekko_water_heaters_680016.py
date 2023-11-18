import pytest
from aiohttp import ClientSession
from aiohttp import web
from PyMyGekko import MyGekkoApiClient
from PyMyGekko.resources.WaterHeaters import WaterHeaterFeature
from PyMyGekko.resources.WaterHeaters import WaterHeaterState


async def var_response(request):
    varResponseFile = open("tests/water_heater/data/api_var_response_680016.json")
    return web.Response(status=200, body=varResponseFile.read())


async def var_status_response(request):
    statusResponseFile = open(
        "tests/water_heater/data/api_var_status_response_680016.json"
    )
    return web.Response(status=200, body=statusResponseFile.read())


@pytest.fixture
def mock_server(aiohttp_server):
    app = web.Application()
    app.router.add_get("/api/v1/var", var_response)
    app.router.add_get("/api/v1/var/status", var_status_response)
    return aiohttp_server(app)


@pytest.mark.asyncio
async def test_get_lights(mock_server):
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
        waterHeaters = api.get_water_heaters()

        assert waterHeaters is not None
        assert len(waterHeaters) == 1

        assert waterHeaters[0].id == "item0"
        assert waterHeaters[0].name == "Warmwasserspeicher"
        assert waterHeaters[0].state == WaterHeaterState.ON
        assert waterHeaters[0].target_temperature == 55.0
        assert waterHeaters[0].current_temperature_bottom == 22.0
        assert waterHeaters[0].current_temperature_top == 61.1
        assert len(waterHeaters[0].supported_features) == 2
        assert WaterHeaterFeature.ON_OFF in waterHeaters[0].supported_features
        assert (
            WaterHeaterFeature.TARGET_TEMPERATURE in waterHeaters[0].supported_features
        )
