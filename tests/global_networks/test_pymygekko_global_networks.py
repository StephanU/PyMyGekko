from aiohttp import ClientSession
from aiohttp import web
from PyMyGekko import MyGekkoApiClient
from pytest import fixture
from pytest import mark


async def var_response(request):
    varResponseFile = open("tests/global_networks/api_var_response.json")
    return web.Response(status=200, body=varResponseFile.read())


async def var_status_response(request):
    statusResponseFile = open("tests/global_networks/api_var_status_response.json")
    return web.Response(status=200, body=statusResponseFile.read())


@fixture
def mock_server(aiohttp_server):
    app = web.Application()
    app.router.add_get("/api/v1/var", var_response)
    app.router.add_get("/api/v1/var/status", var_status_response)
    return aiohttp_server(app)


@mark.asyncio
async def test_get_globals_network(mock_server):
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
        globals_network = api.get_globals_network()

        assert globals_network is not None
        assert globals_network["gekkoname"] == "myGEKKO"
        assert globals_network["language"] == "0"
        assert globals_network["version"] == "596610"
        assert globals_network["hardware"] == "Slide 2 (AC0DFE300913)"
