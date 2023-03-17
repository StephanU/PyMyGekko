import pytest

from aiohttp import web
from PyMyGekko.PyMyGekko import PyMyGekko


async def var_response(request):
    varResponseFile = open("tests/blinds/api_var_response.json")
    return web.Response(status=200, body=varResponseFile.read())


async def var_status_response(request):
    statusResponseFile = open("tests/blinds/api_var_status_response.json")
    return web.Response(status=200, body=statusResponseFile.read())


@pytest.fixture
def mock_server(aiohttp_server):
    app = web.Application()
    app.router.add_get("/api/v1/var", var_response)
    app.router.add_get("/api/v1/var/status", var_status_response)
    return aiohttp_server(app)


@pytest.mark.asyncio
async def test_get_blinds(mock_server):
    server = await mock_server
    api = PyMyGekko(
        "USERNAME",
        "APIKEY",
        "GEKKOID",
        scheme=server.scheme,
        host=server.host,
        port=server.port,
    )

    await api.read_data()
    blinds = api.get_blinds()

    assert blinds != None
    assert len(blinds) == 10

    assert blinds[0]._id == "item0"
    assert blinds[0]._name == "Wohnen Terrasse"
