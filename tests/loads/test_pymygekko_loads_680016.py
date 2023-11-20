import pytest
from aiohttp import ClientSession
from aiohttp import web
from PyMyGekko import MyGekkoApiClient
from PyMyGekko.resources.Loads import LoadFeature
from PyMyGekko.resources.Loads import LoadState


async def var_response(request):
    varResponseFile = open("tests/loads/data/api_var_response_680016.json")
    return web.Response(status=200, body=varResponseFile.read())


async def var_status_response(request):
    statusResponseFile = open("tests/loads/data/api_var_status_response_680016.json")
    return web.Response(status=200, body=statusResponseFile.read())


@pytest.fixture
def mock_server(aiohttp_server):
    app = web.Application()
    app.router.add_get("/api/v1/var", var_response)
    app.router.add_get("/api/v1/var/status", var_status_response)
    return aiohttp_server(app)


@pytest.mark.asyncio
async def test_get_loads(mock_server):
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
        loads = api.get_loads()

        assert loads is not None
        assert len(loads) == 3

        assert loads[0].id == "item0"
        assert loads[0].name == "Balkon Steckdose"
        assert loads[0].state == LoadState.ON_PERMANENT
        assert len(loads[0].supported_features) == 1
        assert LoadFeature.ON_OFF in loads[0].supported_features

        assert loads[1].id == "item1"
        assert loads[1].name == "Terrasse Steckdose"
        assert loads[1].state == LoadState.OFF
        assert len(loads[1].supported_features) == 1
        assert LoadFeature.ON_OFF in loads[1].supported_features

        assert loads[2].id == "item2"
        assert loads[2].name == "HWR Steckdose"
        assert loads[2].state == LoadState.OFF
        assert len(loads[2].supported_features) == 1
        assert LoadFeature.ON_OFF in loads[2].supported_features
