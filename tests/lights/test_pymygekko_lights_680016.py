import pytest
from aiohttp import ClientSession
from aiohttp import web
from PyMyGekko import MyGekkoApiClient
from PyMyGekko.resources.Lights import LightFeature
from PyMyGekko.resources.Lights import LightState


async def var_response(request):
    varResponseFile = open("tests/lights/data/api_var_response_680016.json")
    return web.Response(status=200, body=varResponseFile.read())


async def var_status_response(request):
    statusResponseFile = open("tests/lights/data/api_var_status_response_680016.json")
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
        lights = api.get_lights()

        assert lights is not None
        assert len(lights) == 5

        assert lights[0].id == "item0"
        assert lights[0].name == "Büro 1 Licht"
        assert lights[0].state == LightState.ON
        assert len(lights[0].supported_features) == 1
        assert LightFeature.ON_OFF in lights[0].supported_features

        assert lights[1].id == "item1"
        assert lights[1].name == "Büro 2 Licht"
        assert lights[1].state == LightState.OFF
        assert len(lights[1].supported_features) == 1
        assert LightFeature.ON_OFF in lights[1].supported_features

        assert lights[2].id == "item2"
        assert lights[2].name == "Büro Küche Licht"
        assert lights[2].state == LightState.OFF
        assert len(lights[2].supported_features) == 1
        assert LightFeature.ON_OFF in lights[1].supported_features

        assert lights[3].id == "group0"
        assert lights[3].name == "ALLE"
        assert lights[3].state is None
        assert lights[3].brightness is None
        assert lights[3].rgb_color is None
        assert len(lights[3].supported_features) == 1
        assert LightFeature.ON_OFF in lights[3].supported_features

        assert lights[4].id == "group1"
        assert lights[4].name == "Licht Aussen"
        assert lights[4].state is None
        assert lights[4].brightness is None
        assert lights[4].rgb_color is None
        assert len(lights[3].supported_features) == 1
        assert LightFeature.ON_OFF in lights[4].supported_features
