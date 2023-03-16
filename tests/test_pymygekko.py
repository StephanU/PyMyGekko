import pytest

from aiohttp import web
from PyMyGekko.PyMyGekko import PyMyGekko


async def response(request):
    return web.Response(status=200)


@pytest.fixture
def mock_server(aiohttp_server):
    app = web.Application()
    app.router.add_get("/api/v1/var", response)
    return aiohttp_server(app)


def test_init():
    api = PyMyGekko("username", "apiKey", "gekkoId")

    assert api != None


@pytest.mark.asyncio
async def test_try_connect(mock_server):
    server = await mock_server
    api = PyMyGekko(
        "USERNAME",
        "APIKEY",
        "GEKKOID",
        scheme=server.scheme,
        host=server.host,
        port=server.port,
    )

    response_status = await api.try_connect()
    assert response_status == 200
