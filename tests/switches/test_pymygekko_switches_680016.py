import pytest
from aiohttp import ClientSession
from aiohttp import web
from PyMyGekko import MyGekkoApiClient
from PyMyGekko.resources.Switches import SwitchFeature
from PyMyGekko.resources.Switches import SwitchState


async def var_response(request):
    varResponseFile = open("tests/switches/data/api_var_response_680016.json")
    return web.Response(status=200, body=varResponseFile.read())


async def var_status_response(request):
    statusResponseFile = open("tests/switches/data/api_var_status_response_680016.json")
    return web.Response(status=200, body=statusResponseFile.read())


@pytest.fixture
def mock_server(aiohttp_server):
    app = web.Application()
    app.router.add_get("/api/v1/var", var_response)
    app.router.add_get("/api/v1/var/status", var_status_response)
    return aiohttp_server(app)


@pytest.mark.asyncio
async def test_get_switches(mock_server):
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
        switches = api.get_switches()

        assert switches is not None
        assert len(switches) == 3

        assert switches[0].id == "item0"
        assert switches[0].name == "Balkon Steckdose"
        assert switches[0].state == SwitchState.ON_PERMANENT
        assert len(switches[0].supported_features) == 1
        assert SwitchFeature.ON_OFF in switches[0].supported_features

        assert switches[1].id == "item1"
        assert switches[1].name == "Terrasse Steckdose"
        assert switches[1].state == SwitchState.OFF
        assert len(switches[1].supported_features) == 1
        assert SwitchFeature.ON_OFF in switches[1].supported_features

        assert switches[2].id == "item2"
        assert switches[2].name == "HWR Steckdose"
        assert switches[2].state == SwitchState.OFF
        assert len(switches[2].supported_features) == 1
        assert SwitchFeature.ON_OFF in switches[2].supported_features
