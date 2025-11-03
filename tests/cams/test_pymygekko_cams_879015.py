import logging

import pytest
from aiohttp import ClientSession
from aiohttp import web
from PyMyGekko import MyGekkoApiClientBase
from PyMyGekko.resources.Cams import CamFeature

_LOGGER: logging.Logger = logging.getLogger(__name__)


async def var_response(request):
    varResponseFile = open("tests/cams/data/api_var_response_879015.json")
    return web.Response(status=200, body=varResponseFile.read())


async def var_status_response(request):
    statusResponseFile = open("tests/cams/data/api_var_status_response_879015.json")
    return web.Response(status=200, body=statusResponseFile.read())


@pytest.fixture
def mock_server(aiohttp_server):
    app = web.Application()
    app.router.add_get("/api/v1/var", var_response)
    app.router.add_get("/api/v1/var/status", var_status_response)
    return aiohttp_server(app)


@pytest.mark.asyncio
async def test_get_cams(mock_server):
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
        cams = api.get_cams()

        assert cams is not None
        assert len(cams) == 1

        assert cams[0].entity_id == "item2"
        assert cams[0].name == "DoorBird"
        assert cams[0].image_url == "http://XXX@192.168.1.50/bha-api/image.cgi"
        assert cams[0].stream_url == "http://XXX@192.168.1.50/bha-api/video.cgi"
        assert len(cams[0].supported_features) == 1
        assert CamFeature.STREAM in cams[0].supported_features
