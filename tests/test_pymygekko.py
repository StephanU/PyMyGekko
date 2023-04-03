import pytest
from aiohttp import ClientSession
from aiohttp import web
from PyMyGekko import MyGekkoApiClient


async def response(request):
    return web.Response(status=200)


@pytest.fixture
def mock_server(aiohttp_server):
    app = web.Application()
    app.router.add_get("/api/v1/var", response)
    return aiohttp_server(app)


@pytest.mark.asyncio
async def test_init():
    async with ClientSession() as session:
        api = MyGekkoApiClient("username", "apiKey", "gekkoId", session)

        assert api is not None


@pytest.mark.asyncio
async def test_try_connect(mock_server):
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

        await api.try_connect()
