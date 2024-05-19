import pytest
from aiohttp import ClientSession
from aiohttp import web
from PyMyGekko import MyGekkoApiClientBase


async def var_response(request):
    varResponseFile = open("tests/energy_costs/data/api_var_response_643612.json")
    return web.Response(status=200, body=varResponseFile.read())


async def var_status_response(request):
    statusResponseFile = open(
        "tests/energy_costs/data/api_var_status_response_643612.json"
    )
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
        api = MyGekkoApiClientBase(
            {},
            session,
            scheme=server.scheme,
            host=server.host,
            port=server.port,
        )

        await api.read_data()
        energy_costs = api.get_energy_costs()

        assert energy_costs is not None
        assert len(energy_costs) == 4

        assert energy_costs[0].entity_id == "item0"
        assert energy_costs[0].name == "Meter 1"
        assert len(energy_costs[0].sensor_data) == 2
        assert len(energy_costs[0].sensor_data["values"]) == 20
        assert energy_costs[0].sensor_data["name"] == "Meter 1"

        assert energy_costs[0].sensor_data["values"][0]["name"] == "actPower"
        assert energy_costs[0].sensor_data["values"][0]["unit"] == "kW"
        assert energy_costs[0].sensor_data["values"][0]["value"] == 0.94

        assert energy_costs[0].sensor_data["values"][1]["name"] == "energyToday"
        assert energy_costs[0].sensor_data["values"][1]["unit"] == "kWh"
        assert energy_costs[0].sensor_data["values"][1]["value"] == 0.73

        assert energy_costs[0].sensor_data["values"][2]["name"] == "energyMonth"
        assert energy_costs[0].sensor_data["values"][2]["unit"] == "kWh"
        assert energy_costs[0].sensor_data["values"][2]["value"] == 108.97

        assert energy_costs[1].entity_id == "item1"
        assert energy_costs[1].name == "Meter 2"
        assert len(energy_costs[1].sensor_data) == 2
        assert len(energy_costs[1].sensor_data["values"]) == 20
        assert energy_costs[1].sensor_data["name"] == "Meter 2"

        assert energy_costs[1].sensor_data["values"][0]["name"] == "actPower"
        assert energy_costs[1].sensor_data["values"][0]["unit"] == "kW"
        assert energy_costs[1].sensor_data["values"][0]["value"] == -1.71

        assert energy_costs[1].sensor_data["values"][1]["name"] == "energyToday"
        assert energy_costs[1].sensor_data["values"][1]["unit"] == "kWh"
        assert energy_costs[1].sensor_data["values"][1]["value"] == 2.52

        assert energy_costs[1].sensor_data["values"][2]["name"] == "energyMonth"
        assert energy_costs[1].sensor_data["values"][2]["unit"] == "kWh"
        assert energy_costs[1].sensor_data["values"][2]["value"] == 259.4

        assert energy_costs[2].entity_id == "item2"
        assert energy_costs[2].name == "Photovoltaics"
        assert len(energy_costs[2].sensor_data) == 2
        assert len(energy_costs[2].sensor_data["values"]) == 20
        assert energy_costs[2].sensor_data["name"] == "Photovoltaics"

        assert energy_costs[2].sensor_data["values"][0]["name"] == "actPower"
        assert energy_costs[2].sensor_data["values"][0]["unit"] == "kW"
        assert energy_costs[2].sensor_data["values"][0]["value"] == -3.03

        assert energy_costs[2].sensor_data["values"][1]["name"] == "energyToday"
        assert energy_costs[2].sensor_data["values"][1]["unit"] == "kWh"
        assert energy_costs[2].sensor_data["values"][1]["value"] == 0.07

        assert energy_costs[2].sensor_data["values"][2]["name"] == "energyMonth"
        assert energy_costs[2].sensor_data["values"][2]["unit"] == "kWh"
        assert energy_costs[2].sensor_data["values"][2]["value"] == 3.0

        assert energy_costs[3].entity_id == "item3"
        assert energy_costs[3].name == "Swimming Pool"
        assert len(energy_costs[3].sensor_data) == 2
        assert len(energy_costs[3].sensor_data["values"]) == 20
        assert energy_costs[3].sensor_data["name"] == "Swimming Pool"

        assert energy_costs[3].sensor_data["values"][0]["name"] == "actPower"
        assert energy_costs[3].sensor_data["values"][0]["unit"] == "kW"
        assert energy_costs[3].sensor_data["values"][0]["value"] == 0.01

        assert energy_costs[3].sensor_data["values"][1]["name"] == "energyToday"
        assert energy_costs[3].sensor_data["values"][1]["unit"] == "kWh"
        assert energy_costs[3].sensor_data["values"][1]["value"] == 0.08

        assert energy_costs[3].sensor_data["values"][2]["name"] == "energyMonth"
        assert energy_costs[3].sensor_data["values"][2]["unit"] == "kWh"
        assert energy_costs[3].sensor_data["values"][2]["value"] == 60.92
