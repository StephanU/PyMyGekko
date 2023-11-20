import pytest
from aiohttp import ClientSession
from aiohttp import web
from PyMyGekko import MyGekkoApiClient
from PyMyGekko.resources.RoomTemps import RoomTempsFeature
from PyMyGekko.resources.RoomTemps import RoomTempsMode


async def var_response(request):
    varResponseFile = open("tests/room_temps/data/api_var_response_680016.json")
    return web.Response(status=200, body=varResponseFile.read())


async def var_status_response(request):
    statusResponseFile = open(
        "tests/room_temps/data/api_var_status_response_680016.json"
    )
    return web.Response(status=200, body=statusResponseFile.read())


@pytest.fixture
def mock_server(aiohttp_server):
    app = web.Application()
    app.router.add_get("/api/v1/var", var_response)
    app.router.add_get("/api/v1/var/status", var_status_response)
    return aiohttp_server(app)


@pytest.mark.asyncio
async def test_get_room_temps(mock_server):
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
        roomTemps = api.get_room_temps()

        assert roomTemps is not None
        assert len(roomTemps) == 5

        assert roomTemps[0].id == "item0"
        assert roomTemps[0].name == "WohnenKüche"
        assert roomTemps[0].target_temperature == 21.3
        assert roomTemps[0].working_mode == RoomTempsMode.Comfort
        assert len(roomTemps[0].supported_features) == 1
        assert RoomTempsFeature.TARGET_TEMPERATURE in roomTemps[0].supported_features

        assert roomTemps[1].id == "item1"
        assert roomTemps[1].name == "Speisekammer"
        assert roomTemps[1].target_temperature == 18.00
        assert roomTemps[1].working_mode == RoomTempsMode.Comfort
        assert len(roomTemps[1].supported_features) == 1
        assert RoomTempsFeature.TARGET_TEMPERATURE in roomTemps[1].supported_features

        assert roomTemps[2].id == "item2"
        assert roomTemps[2].name == "HWR"
        assert roomTemps[2].target_temperature == 20.00
        assert roomTemps[2].working_mode == RoomTempsMode.Comfort
        assert len(roomTemps[2].supported_features) == 1
        assert RoomTempsFeature.TARGET_TEMPERATURE in roomTemps[2].supported_features

        assert roomTemps[3].id == "item3"
        assert roomTemps[3].name == "WC EG"
        assert roomTemps[3].target_temperature == 22.00
        assert roomTemps[3].working_mode == RoomTempsMode.Comfort
        assert len(roomTemps[3].supported_features) == 1
        assert RoomTempsFeature.TARGET_TEMPERATURE in roomTemps[3].supported_features

        assert roomTemps[4].id == "item4"
        assert roomTemps[4].name == "Gast"
        assert roomTemps[4].target_temperature == 17.00
        assert roomTemps[4].working_mode == RoomTempsMode.Reduced
        assert len(roomTemps[4].supported_features) == 1
        assert RoomTempsFeature.TARGET_TEMPERATURE in roomTemps[4].supported_features
