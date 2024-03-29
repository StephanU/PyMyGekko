import pytest
from aiohttp import ClientSession
from aiohttp import web
from PyMyGekko import MyGekkoApiClientBase
from PyMyGekko.resources.RoomTemps import RoomTempsFeature
from PyMyGekko.resources.RoomTemps import RoomTempsMode


async def var_response(request):
    varResponseFile = open("tests/room_temps/data/api_var_response_596610.json")
    return web.Response(status=200, body=varResponseFile.read())


async def var_status_response(request):
    statusResponseFile = open(
        "tests/room_temps/data/api_var_status_response_596610.json"
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
        api = MyGekkoApiClientBase(
            {},
            session,
            scheme=server.scheme,
            host=server.host,
            port=server.port,
        )

        await api.read_data()
        roomTemps = api.get_room_temps()

        assert roomTemps is not None
        assert len(roomTemps) == 8

        assert roomTemps[0].entity_id == "item0"
        assert roomTemps[0].name == "WZ"
        assert roomTemps[0].target_temperature == 22.00
        assert roomTemps[0].working_mode == RoomTempsMode.COMFORT
        assert roomTemps[0].humidity == 33.1
        assert len(roomTemps[0].supported_features) == 2
        assert RoomTempsFeature.TARGET_TEMPERATURE in roomTemps[0].supported_features
        assert RoomTempsFeature.HUMIDITY in roomTemps[0].supported_features

        assert roomTemps[1].entity_id == "item1"
        assert roomTemps[1].name == "Flur"
        assert roomTemps[1].target_temperature == 18.00
        assert roomTemps[1].working_mode == RoomTempsMode.REDUCED
        assert roomTemps[1].humidity == 33.3
        assert len(roomTemps[1].supported_features) == 2
        assert RoomTempsFeature.TARGET_TEMPERATURE in roomTemps[1].supported_features
        assert RoomTempsFeature.HUMIDITY in roomTemps[1].supported_features

        assert roomTemps[2].entity_id == "item2"
        assert roomTemps[2].name == "WC"
        assert roomTemps[2].target_temperature == 21.00
        assert roomTemps[2].working_mode == RoomTempsMode.COMFORT
        assert roomTemps[2].humidity == 35.2
        assert len(roomTemps[2].supported_features) == 2
        assert RoomTempsFeature.TARGET_TEMPERATURE in roomTemps[2].supported_features
        assert RoomTempsFeature.HUMIDITY in roomTemps[2].supported_features

        assert roomTemps[3].entity_id == "item3"
        assert roomTemps[3].name == "Arbeiten"
        assert roomTemps[3].target_temperature == 19.00
        assert roomTemps[3].working_mode == RoomTempsMode.REDUCED
        assert roomTemps[3].humidity == 35.3
        assert len(roomTemps[3].supported_features) == 2
        assert RoomTempsFeature.TARGET_TEMPERATURE in roomTemps[3].supported_features
        assert RoomTempsFeature.HUMIDITY in roomTemps[3].supported_features

        assert roomTemps[4].entity_id == "item4"
        assert roomTemps[4].name == "Schlafen"
        assert roomTemps[4].target_temperature == 19.00
        assert roomTemps[4].working_mode == RoomTempsMode.REDUCED
        assert roomTemps[4].humidity == 36.6
        assert len(roomTemps[4].supported_features) == 2
        assert RoomTempsFeature.TARGET_TEMPERATURE in roomTemps[4].supported_features
        assert RoomTempsFeature.HUMIDITY in roomTemps[4].supported_features

        assert roomTemps[5].entity_id == "item5"
        assert roomTemps[5].name == "Kind 1"
        assert roomTemps[5].target_temperature == 21.00
        assert roomTemps[5].working_mode == RoomTempsMode.COMFORT
        assert roomTemps[5].humidity == 31.4
        assert len(roomTemps[5].supported_features) == 2
        assert RoomTempsFeature.TARGET_TEMPERATURE in roomTemps[5].supported_features
        assert RoomTempsFeature.HUMIDITY in roomTemps[5].supported_features

        assert roomTemps[6].entity_id == "item6"
        assert roomTemps[6].name == "Kind 2"
        assert roomTemps[6].target_temperature == 21.50
        assert roomTemps[6].working_mode == RoomTempsMode.REDUCED
        assert roomTemps[6].humidity == 33.5
        assert len(roomTemps[6].supported_features) == 2
        assert RoomTempsFeature.TARGET_TEMPERATURE in roomTemps[6].supported_features
        assert RoomTempsFeature.HUMIDITY in roomTemps[6].supported_features

        assert roomTemps[7].entity_id == "item7"
        assert roomTemps[7].name == "Bad OG"
        assert roomTemps[7].target_temperature == 21.00
        assert roomTemps[7].working_mode == RoomTempsMode.REDUCED
        assert roomTemps[7].humidity == 38.6
        assert len(roomTemps[7].supported_features) == 2
        assert RoomTempsFeature.TARGET_TEMPERATURE in roomTemps[7].supported_features
        assert RoomTempsFeature.HUMIDITY in roomTemps[7].supported_features
