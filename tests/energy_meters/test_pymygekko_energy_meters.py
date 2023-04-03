import pytest
from aiohttp import ClientSession
from aiohttp import web
from PyMyGekko import MyGekkoApiClient


async def var_response(request):
    varResponseFile = open("tests/energy_meters/api_var_response.json")
    return web.Response(status=200, body=varResponseFile.read())


async def var_status_response(request):
    statusResponseFile = open("tests/energy_meters/api_var_status_response.json")
    return web.Response(status=200, body=statusResponseFile.read())


@pytest.fixture
def mock_server(aiohttp_server):
    app = web.Application()
    app.router.add_get("/api/v1/var", var_response)
    app.router.add_get("/api/v1/var/status", var_status_response)
    return aiohttp_server(app)


@pytest.mark.asyncio
async def test_get_energy_meters(mock_server):
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
        energy_meters = api.get_energy_meters()

        assert energy_meters is not None
        assert len(energy_meters) == 2

        assert energy_meters[0].id == "item0"
        assert energy_meters[0].name == "Hauptstromzähler"
        assert len(energy_meters[0].sensor_data) == 2
        assert len(energy_meters[0].sensor_data["values"]) == 20

        assert energy_meters[1].id == "item1"
        assert energy_meters[1].name == "Wärmemengenzähler"
