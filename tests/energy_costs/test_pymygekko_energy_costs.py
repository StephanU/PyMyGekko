import pytest
from aiohttp import ClientSession
from aiohttp import web
from PyMyGekko import MyGekkoApiClient


async def var_response(request):
    varResponseFile = open("tests/energy_costs/api_var_response.json")
    return web.Response(status=200, body=varResponseFile.read())


async def var_status_response(request):
    statusResponseFile = open("tests/energy_costs/api_var_status_response.json")
    return web.Response(status=200, body=statusResponseFile.read())


@pytest.fixture
def mock_server(aiohttp_server):
    app = web.Application()
    app.router.add_get("/api/v1/var", var_response)
    app.router.add_get("/api/v1/var/status", var_status_response)
    return aiohttp_server(app)


@pytest.mark.asyncio
async def test_get_energy_costs(mock_server):
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
        energy_costs = api.get_energy_costs()

        assert energy_costs is not None
        assert len(energy_costs) == 2

        assert energy_costs[0].id == "item0"
        assert energy_costs[0].name == "Hauptstromzähler"
        assert len(energy_costs[0].sensor_data) == 2
        assert len(energy_costs[0].sensor_data["values"]) == 20
        assert energy_costs[0].sensor_data["name"] == "Hauptstromzähler"

        assert energy_costs[0].sensor_data["values"][0]["name"] == "actPower"
        assert energy_costs[0].sensor_data["values"][0]["unit"] == "kW"
        assert energy_costs[0].sensor_data["values"][0]["value"] == 0.11

        assert energy_costs[0].sensor_data["values"][1]["name"] == "energyToday"
        assert energy_costs[0].sensor_data["values"][1]["unit"] == "kWh"
        assert energy_costs[0].sensor_data["values"][1]["value"] == 12.3

        assert energy_costs[0].sensor_data["values"][2]["name"] == "energyMonth"
        assert energy_costs[0].sensor_data["values"][2]["unit"] == "kWh"
        assert energy_costs[0].sensor_data["values"][2]["value"] == 113.6

        assert energy_costs[1].id == "item1"
        assert energy_costs[1].name == "Wärmemengenzähler"
        assert len(energy_costs[1].sensor_data) == 2
        assert len(energy_costs[1].sensor_data["values"]) == 20
        assert energy_costs[1].sensor_data["name"] == "Wärmemengenzähler"

        assert energy_costs[1].sensor_data["values"][0]["name"] == "actPower"
        assert energy_costs[1].sensor_data["values"][0]["unit"] == "kW"
        assert energy_costs[1].sensor_data["values"][0]["value"] == 0.7

        assert energy_costs[1].sensor_data["values"][1]["name"] == "energyToday"
        assert energy_costs[1].sensor_data["values"][1]["unit"] == "kWh"
        assert energy_costs[1].sensor_data["values"][1]["value"] == 19.0

        assert energy_costs[1].sensor_data["values"][2]["name"] == "energyMonth"
        assert energy_costs[1].sensor_data["values"][2]["unit"] == "kWh"
        assert energy_costs[1].sensor_data["values"][2]["value"] == 338.0
