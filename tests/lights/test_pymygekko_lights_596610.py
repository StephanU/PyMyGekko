import pytest
from aiohttp import ClientSession
from aiohttp import web
from PyMyGekko import MyGekkoApiClientBase
from PyMyGekko.resources.Lights import LightFeature
from PyMyGekko.resources.Lights import LightState


async def var_response(request):
    varResponseFile = open("tests/lights/data/api_var_response_596610.json")
    return web.Response(status=200, body=varResponseFile.read())


async def var_status_response(request):
    statusResponseFile = open("tests/lights/data/api_var_status_response_596610.json")
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
        api = MyGekkoApiClientBase(
            {},
            session,
            scheme=server.scheme,
            host=server.host,
            port=server.port,
        )

        await api.read_data()
        lights = api.get_lights()

        assert lights is not None
        assert len(lights) == 4

        assert lights[0].entity_id == "item0"
        assert lights[0].name == "Aussen"
        assert lights[0].state == LightState.ON
        assert len(lights[0].supported_features) == 1
        assert LightFeature.ON_OFF in lights[0].supported_features

        assert lights[1].entity_id == "item1"
        assert lights[1].name == "Aussen2"
        assert lights[1].state == LightState.ON
        assert lights[1].brightness == 50
        assert len(lights[1].supported_features) == 2
        assert LightFeature.ON_OFF in lights[1].supported_features
        assert LightFeature.DIMMABLE in lights[1].supported_features

        assert lights[2].entity_id == "item2"
        assert lights[2].name == "Aussen3"
        assert lights[2].state == LightState.OFF
        assert lights[2].brightness == 44
        assert lights[2].rgb_color == (255, 0, 39)
        assert len(lights[2].supported_features) == 3
        assert LightFeature.ON_OFF in lights[2].supported_features
        assert LightFeature.DIMMABLE in lights[2].supported_features
        assert LightFeature.RGB_COLOR in lights[2].supported_features

        assert lights[3].entity_id == "group0"
        assert lights[3].name == "alle"
        assert lights[3].state == LightState.ON
        assert lights[3].brightness is None
        assert lights[3].rgb_color is None
        assert len(lights[3].supported_features) == 1
        assert LightFeature.ON_OFF in lights[3].supported_features
