import pytest
from aiohttp import ClientSession
from aiohttp import web
from PyMyGekko import MyGekkoApiClientBase
from PyMyGekko.resources.RoomTemps import RoomTempsFeature
from PyMyGekko.resources.RoomTemps import RoomTempsMode


async def var_response(request):
    varResponseFile = open("tests/room_temps/data/api_var_response_slide.json")
    return web.Response(status=200, body=varResponseFile.read())


async def var_status_response(request):
    statusResponseFile = open(
        "tests/room_temps/data/api_var_status_response_slide.json"
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
        assert len(roomTemps) == 7

        assert roomTemps[0].entity_id == "item0"
        assert roomTemps[0].name == "Wohnen"
        assert roomTemps[0].current_temperature == 23.94000053405762
        assert roomTemps[0].target_temperature == 22.00
        assert roomTemps[0].working_mode == RoomTempsMode.REDUCED
        assert roomTemps[0].humidity is None
        assert len(roomTemps[0].supported_features) == 1
        assert RoomTempsFeature.TARGET_TEMPERATURE in roomTemps[0].supported_features

        assert roomTemps[1].entity_id == "item1"
        assert roomTemps[1].name == "Gäste-Wc"
        assert roomTemps[1].current_temperature == 22.5
        assert roomTemps[1].target_temperature == 22.00
        assert roomTemps[1].working_mode == RoomTempsMode.REDUCED
        assert roomTemps[1].humidity is None
        assert len(roomTemps[1].supported_features) == 1
        assert RoomTempsFeature.TARGET_TEMPERATURE in roomTemps[1].supported_features

        assert roomTemps[2].entity_id == "item2"
        assert roomTemps[2].name == "Kind 1"
        assert roomTemps[2].current_temperature == 23.61999893188477
        assert roomTemps[2].target_temperature == 19.00
        assert roomTemps[2].working_mode == RoomTempsMode.REDUCED
        assert roomTemps[2].humidity is None
        assert len(roomTemps[2].supported_features) == 1
        assert RoomTempsFeature.TARGET_TEMPERATURE in roomTemps[2].supported_features

        assert roomTemps[3].entity_id == "item3"
        assert roomTemps[3].name == "Schlafzimmer"
        assert roomTemps[3].current_temperature == 21.95000076293945
        assert roomTemps[3].target_temperature == 22.00
        assert roomTemps[3].working_mode == RoomTempsMode.REDUCED
        assert roomTemps[3].humidity is None
        assert len(roomTemps[3].supported_features) == 1
        assert RoomTempsFeature.TARGET_TEMPERATURE in roomTemps[3].supported_features

        assert roomTemps[4].entity_id == "item4"
        assert roomTemps[4].name == "Kind 2"
        assert roomTemps[4].current_temperature == 24.97999954223633
        assert roomTemps[4].target_temperature == 23.00
        assert roomTemps[4].working_mode == RoomTempsMode.REDUCED
        assert roomTemps[4].humidity is None
        assert len(roomTemps[4].supported_features) == 1
        assert RoomTempsFeature.TARGET_TEMPERATURE in roomTemps[4].supported_features

        assert roomTemps[5].entity_id == "item5"
        assert roomTemps[5].name == "Kind 3"
        assert roomTemps[5].current_temperature == 22.81599998474121
        assert roomTemps[5].target_temperature == 21.00
        assert roomTemps[5].working_mode == RoomTempsMode.REDUCED
        assert roomTemps[5].humidity is None
        assert len(roomTemps[5].supported_features) == 1
        assert RoomTempsFeature.TARGET_TEMPERATURE in roomTemps[5].supported_features

        assert roomTemps[6].entity_id == "item6"
        assert roomTemps[6].name == "Bad"
        assert roomTemps[6].current_temperature == 24.07999992370605
        assert roomTemps[6].target_temperature == 22.0
        assert roomTemps[6].working_mode == RoomTempsMode.REDUCED
        assert roomTemps[6].humidity is None
        assert len(roomTemps[6].supported_features) == 1
        assert RoomTempsFeature.TARGET_TEMPERATURE in roomTemps[6].supported_features
