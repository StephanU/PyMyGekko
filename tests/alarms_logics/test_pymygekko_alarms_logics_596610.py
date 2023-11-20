import pytest
from aiohttp import ClientSession
from aiohttp import web
from PyMyGekko import MyGekkoApiClient


async def var_response(request):
    varResponseFile = open("tests/alarms_logics/data/api_var_response_596610.json")
    return web.Response(status=200, body=varResponseFile.read())


async def var_status_response(request):
    statusResponseFile = open(
        "tests/alarms_logics/data/api_var_status_response_596610.json"
    )
    return web.Response(status=200, body=statusResponseFile.read())


@pytest.fixture
def mock_server(aiohttp_server):
    app = web.Application()
    app.router.add_get("/api/v1/var", var_response)
    app.router.add_get("/api/v1/var/status", var_status_response)
    return aiohttp_server(app)


@pytest.mark.asyncio
async def test_get_alarms_logics(mock_server):
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
        alarms_logics = api.get_alarms_logics()

        assert alarms_logics is not None
        assert len(alarms_logics) == 2

        assert alarms_logics[0].id == "item0"
        assert alarms_logics[0].name == "Button"
        assert alarms_logics[0].value == 1.0

        assert alarms_logics[1].id == "item15"
        assert alarms_logics[1].name == "Klingel"
        assert alarms_logics[1].value == 0.0
