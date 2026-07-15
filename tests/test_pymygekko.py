import pytest
from aiohttp import ClientSession
from aiohttp import web
from PyMyGekko import MyGekkoApiClientBase


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
        api = MyGekkoApiClientBase("username", "apiKey", "gekkoId", session)

        assert api is not None


@pytest.mark.asyncio
async def test_try_connect(mock_server):
    server = await mock_server
    async with ClientSession() as session:
        api = MyGekkoApiClientBase(
            {},
            session,
            scheme=server.scheme,
            host=server.host,
            port=server.port,
        )

        await api.try_connect()


@pytest.mark.asyncio
async def test_read_data_reads_resources_only_once(aiohttp_server):
    request_count = {"var": 0, "status": 0}

    async def var_response(request):
        request_count["var"] += 1
        return web.Response(status=200, body='{"globals": {"network": {}}}')

    async def var_status_response(request):
        request_count["status"] += 1
        return web.Response(status=200, body='{"globals": {"network": {}}}')

    app = web.Application()
    app.router.add_get("/api/v1/var", var_response)
    app.router.add_get("/api/v1/var/status", var_status_response)
    server = await aiohttp_server(app)

    async with ClientSession() as session:
        api = MyGekkoApiClientBase(
            {},
            session,
            scheme=server.scheme,
            host=server.host,
            port=server.port,
        )

        await api.read_data()
        await api.read_data()

        assert request_count["var"] == 1
        assert request_count["status"] == 2
