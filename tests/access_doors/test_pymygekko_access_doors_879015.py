import logging

import pytest
from aiohttp import ClientSession
from aiohttp import web
from PyMyGekko import MyGekkoApiClientBase
from PyMyGekko.resources.AccessDoors import AccessDoorElementInfo
from PyMyGekko.resources.AccessDoors import AccessDoorFeature
from PyMyGekko.resources.AccessDoors import AccessDoorState

_LOGGER: logging.Logger = logging.getLogger(__name__)


async def var_response(request):
    varResponseFile = open("tests/access_doors/data/api_var_response_879015.json")
    return web.Response(status=200, body=varResponseFile.read())


async def var_status_response(request):
    statusResponseFile = open(
        "tests/access_doors/data/api_var_status_response_879015.json"
    )
    return web.Response(status=200, body=statusResponseFile.read())


@pytest.fixture
def mock_server(aiohttp_server):
    app = web.Application()
    app.router.add_get("/api/v1/var", var_response)
    app.router.add_get("/api/v1/var/status", var_status_response)
    return aiohttp_server(app)


@pytest.mark.asyncio
async def test_get_access_doors(mock_server):
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
        doors = api.get_access_doors()

        assert doors is not None
        assert len(doors) == 1

        assert doors[0].entity_id == "item0"
        assert doors[0].name == "Türöffner"
        assert doors[0].access_state == AccessDoorState.CLOSE
        assert doors[0].element_info == AccessDoorElementInfo.OK
        assert len(doors[0].supported_features) == 1
        assert AccessDoorFeature.OPEN in doors[0].supported_features
