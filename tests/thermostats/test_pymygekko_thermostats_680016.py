import pytest
from aiohttp import ClientSession
from aiohttp import web
from PyMyGekko import MyGekkoApiClient
from PyMyGekko.resources.Thermostats import ThermostatFeature
from PyMyGekko.resources.Thermostats import ThermostatMode


async def var_response(request):
    varResponseFile = open("tests/thermostats/data/api_var_response_680016.json")
    return web.Response(status=200, body=varResponseFile.read())


async def var_status_response(request):
    statusResponseFile = open(
        "tests/thermostats/data/api_var_status_response_680016.json"
    )
    return web.Response(status=200, body=statusResponseFile.read())


@pytest.fixture
def mock_server(aiohttp_server):
    app = web.Application()
    app.router.add_get("/api/v1/var", var_response)
    app.router.add_get("/api/v1/var/status", var_status_response)
    return aiohttp_server(app)


@pytest.mark.asyncio
async def test_get_thermostats(mock_server):
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
        thermostats = api.get_thermostats()

        assert thermostats is not None
        assert len(thermostats) == 5

        assert thermostats[0].id == "item0"
        assert thermostats[0].name == "WohnenKüche"
        assert thermostats[0].target_temperature == 21.3
        assert thermostats[0].mode == ThermostatMode.Comfort
        assert len(thermostats[0].supported_features) == 1
        assert ThermostatFeature.TARGET_TEMPERATURE in thermostats[0].supported_features

        assert thermostats[1].id == "item1"
        assert thermostats[1].name == "Speisekammer"
        assert thermostats[1].target_temperature == 18.00
        assert thermostats[1].mode == ThermostatMode.Comfort
        assert len(thermostats[1].supported_features) == 1
        assert ThermostatFeature.TARGET_TEMPERATURE in thermostats[1].supported_features

        assert thermostats[2].id == "item2"
        assert thermostats[2].name == "HWR"
        assert thermostats[2].target_temperature == 20.00
        assert thermostats[2].mode == ThermostatMode.Comfort
        assert len(thermostats[2].supported_features) == 1
        assert ThermostatFeature.TARGET_TEMPERATURE in thermostats[2].supported_features

        assert thermostats[3].id == "item3"
        assert thermostats[3].name == "WC EG"
        assert thermostats[3].target_temperature == 22.00
        assert thermostats[3].mode == ThermostatMode.Comfort
        assert len(thermostats[3].supported_features) == 1
        assert ThermostatFeature.TARGET_TEMPERATURE in thermostats[3].supported_features

        assert thermostats[4].id == "item4"
        assert thermostats[4].name == "Gast"
        assert thermostats[4].target_temperature == 17.00
        assert thermostats[4].mode == ThermostatMode.Reduced
        assert len(thermostats[4].supported_features) == 1
        assert ThermostatFeature.TARGET_TEMPERATURE in thermostats[4].supported_features
