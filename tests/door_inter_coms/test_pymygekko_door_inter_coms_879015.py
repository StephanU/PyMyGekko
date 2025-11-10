import logging

import pytest
from aiohttp import ClientSession
from aiohttp import web
from PyMyGekko import MyGekkoApiClientBase
from PyMyGekko.resources.DoorInterComs import DoorInterComConnectionState
from PyMyGekko.resources.DoorInterComs import DoorInterComSoundMode

_LOGGER: logging.Logger = logging.getLogger(__name__)


async def var_response(request):
    varResponseFile = open("tests/door_inter_coms/data/api_var_response_879015.json")
    return web.Response(status=200, body=varResponseFile.read())


async def var_status_response(request):
    statusResponseFile = open(
        "tests/door_inter_coms/data/api_var_status_response_879015.json"
    )
    return web.Response(status=200, body=statusResponseFile.read())


@pytest.fixture
def mock_server(aiohttp_server):
    app = web.Application()
    app.router.add_get("/api/v1/var", var_response)
    app.router.add_get("/api/v1/var/status", var_status_response)
    return aiohttp_server(app)


@pytest.mark.asyncio
async def test_get_door_inter_coms(mock_server):
    _LOGGER.setLevel(logging.DEBUG)

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
        door_inter_coms = api.get_door_inter_coms()

        assert door_inter_coms is not None
        assert len(door_inter_coms) == 1

        assert door_inter_coms[0].entity_id == "item1"
        assert door_inter_coms[0].name == "2n"
        assert (
            door_inter_coms[0].image_url
            == "http://XXX.XXX.10.XXX/api/camera/snapshot?width=640&height=480"
        )
        assert (
            door_inter_coms[0].stream_url
            == "http://XXX.XXX.10.XXX/api/camera/snapshot?width=640&height=480&fps=15"
        )
        assert door_inter_coms[0].action_on_ring_state is None
        assert door_inter_coms[0].connection_state == DoorInterComConnectionState.OK
        assert door_inter_coms[0].last_missed_call_date is None
        assert door_inter_coms[0].missed_calls == 0
        assert door_inter_coms[0].sound_mode == DoorInterComSoundMode.RINGING
