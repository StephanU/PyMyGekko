import logging

import pytest
from aiohttp import ClientSession
from aiohttp import web
from PyMyGekko import MyGekkoApiClient
from PyMyGekko.resources.Blinds import BlindFeature
from PyMyGekko.resources.Blinds import BlindState

_LOGGER: logging.Logger = logging.getLogger(__name__)


async def var_response(request):
    varResponseFile = open("tests/blinds/data/api_var_response_680016.json")
    return web.Response(status=200, body=varResponseFile.read())


async def var_status_response(request):
    statusResponseFile = open("tests/blinds/data/api_var_status_response_680016.json")
    return web.Response(status=200, body=statusResponseFile.read())


@pytest.fixture
def mock_server(aiohttp_server):
    app = web.Application()
    app.router.add_get("/api/v1/var", var_response)
    app.router.add_get("/api/v1/var/status", var_status_response)
    return aiohttp_server(app)


@pytest.mark.asyncio
async def test_get_blinds(mock_server):
    _LOGGER.setLevel(logging.DEBUG)

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
        blinds = api.get_blinds()

        assert blinds is not None
        assert len(blinds) == 18

        assert blinds[0].id == "item1"
        assert blinds[0].name == "Rollo Schlafzimmer links"
        assert blinds[0].position == 100.00
        assert blinds[0].tilt_position is None
        assert blinds[0].state == BlindState.STOP
        assert len(blinds[0].supported_features) == 2
        assert BlindFeature.OPEN_CLOSE_STOP in blinds[0].supported_features
        assert BlindFeature.SET_POSITION in blinds[0].supported_features

        assert blinds[1].id == "item2"
        assert blinds[1].name == "Rollo Schlafzimmer rechts"
        assert blinds[1].position == 0.31
        assert blinds[1].tilt_position is None
        assert blinds[1].state == BlindState.STOP
        assert len(blinds[1].supported_features) == 2
        assert BlindFeature.OPEN_CLOSE_STOP in blinds[1].supported_features
        assert BlindFeature.SET_POSITION in blinds[1].supported_features

        assert blinds[2].id == "item3"
        assert blinds[2].name == "Rollo Ankleidezimmer"
        assert blinds[2].position == 0.0
        assert blinds[2].tilt_position is None
        assert blinds[2].state == BlindState.STOP
        assert len(blinds[2].supported_features) == 2
        assert BlindFeature.OPEN_CLOSE_STOP in blinds[2].supported_features
        assert BlindFeature.SET_POSITION in blinds[2].supported_features

        assert blinds[3].id == "item4"
        assert blinds[3].name == "Rollo Abstellkammer Ost"
        assert blinds[3].position == 0.3
        assert blinds[3].tilt_position is None
        assert blinds[3].state == BlindState.STOP
        assert len(blinds[3].supported_features) == 2
        assert BlindFeature.OPEN_CLOSE_STOP in blinds[3].supported_features
        assert BlindFeature.SET_POSITION in blinds[3].supported_features

        assert blinds[4].id == "item5"
        assert blinds[4].name == "Rollo Abstellkammer Nord"
        assert blinds[4].position == 0.0
        assert blinds[4].tilt_position is None
        assert blinds[4].state == BlindState.STOP
        assert len(blinds[4].supported_features) == 2
        assert BlindFeature.OPEN_CLOSE_STOP in blinds[4].supported_features
        assert BlindFeature.SET_POSITION in blinds[4].supported_features

        assert blinds[5].id == "item6"
        assert blinds[5].name == "Rollo Kind1 Süd"
        assert blinds[5].position == 0.42
        assert blinds[5].tilt_position is None
        assert blinds[5].state == BlindState.STOP
        assert len(blinds[5].supported_features) == 2
        assert BlindFeature.OPEN_CLOSE_STOP in blinds[5].supported_features
        assert BlindFeature.SET_POSITION in blinds[5].supported_features

        assert blinds[6].id == "item7"
        assert blinds[6].name == "Rollo Kind1 Ost"
        assert blinds[6].position == 0.0
        assert blinds[6].tilt_position is None
        assert blinds[6].state == BlindState.DOWN
        assert len(blinds[6].supported_features) == 2
        assert BlindFeature.OPEN_CLOSE_STOP in blinds[6].supported_features
        assert BlindFeature.SET_POSITION in blinds[6].supported_features

        assert blinds[7].id == "item8"
        assert blinds[7].name == "Rollo Badezimmer OG West"
        assert blinds[7].position == 0.0
        assert blinds[7].tilt_position is None
        assert blinds[7].state == BlindState.STOP
        assert len(blinds[7].supported_features) == 2
        assert BlindFeature.OPEN_CLOSE_STOP in blinds[7].supported_features
        assert BlindFeature.SET_POSITION in blinds[7].supported_features

        assert blinds[8].id == "item9"
        assert blinds[8].name == "Rollo Badezimmer OG Süd"
        assert blinds[8].position == 0.42
        assert blinds[8].tilt_position is None
        assert blinds[8].state == BlindState.STOP
        assert len(blinds[8].supported_features) == 2
        assert BlindFeature.OPEN_CLOSE_STOP in blinds[8].supported_features
        assert BlindFeature.SET_POSITION in blinds[8].supported_features

        assert blinds[9].id == "group0"
        assert blinds[9].name == "EG"
        assert blinds[9].position is None
        assert blinds[9].tilt_position is None
        assert blinds[9].state is None
        await blinds[9].set_state(BlindState.UP)
        assert len(blinds[9].supported_features) == 1
        assert BlindFeature.OPEN_CLOSE in blinds[9].supported_features

        assert blinds[10].id == "group1"
        assert blinds[10].name == "OG"
        assert blinds[10].position is None
        assert blinds[10].tilt_position is None
        assert blinds[10].state is None
        assert len(blinds[10].supported_features) == 1
        assert BlindFeature.OPEN_CLOSE in blinds[10].supported_features
