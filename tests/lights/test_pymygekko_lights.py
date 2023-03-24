from PyMyGekko.resources.Lights import LightState
import pytest

from aiohttp import web, ClientSession
from PyMyGekko import MyGekkoApiClient


async def var_response(request):
    varResponseFile = open("tests/lights/api_var_response.json")
    return web.Response(status=200, body=varResponseFile.read())


async def var_status_response(request):
    statusResponseFile = open("tests/lights/api_var_status_response.json")
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

        assert lights != None
        assert len(lights) == 1

        assert lights[0].id == "item0"
        assert lights[0].name == "Aussen"
        assert lights[0].state == LightState.ON
