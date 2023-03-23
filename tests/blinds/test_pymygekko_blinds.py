from PyMyGekko.resources.Blinds import BlindState
import pytest

from aiohttp import web, ClientSession
from PyMyGekko import MyGekkoApiClient


async def var_response(request):
    varResponseFile = open("tests/blinds/api_var_response.json")
    return web.Response(status=200, body=varResponseFile.read())


async def var_status_response(request):
    statusResponseFile = open("tests/blinds/api_var_status_response.json")
    return web.Response(status=200, body=statusResponseFile.read())


@pytest.fixture
def mock_server(aiohttp_server):
    app = web.Application()
    app.router.add_get("/api/v1/var", var_response)
    app.router.add_get("/api/v1/var/status", var_status_response)
    return aiohttp_server(app)


@pytest.mark.asyncio
async def test_get_blinds(mock_server):
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

        assert blinds != None
        assert len(blinds) == 10

        assert blinds[0].id == "item0"
        assert blinds[0].name == "Wohnen Terrasse"
        assert blinds[0].position == 100.00
        assert blinds[0].state == BlindState.STOP

        assert blinds[1].id == "item1"
        assert blinds[1].name == "Wohnen Fenster"
        assert blinds[1].position == 100.00
        assert blinds[1].state == BlindState.STOP

        assert blinds[2].id == "item2"
        assert blinds[2].name == "Essen"
        assert blinds[2].position == 100.00
        assert blinds[2].state == BlindState.STOP

        assert blinds[3].id == "item3"
        assert blinds[3].name == "Küche"
        assert blinds[3].position == 100.00
        assert blinds[3].state == BlindState.STOP

        assert blinds[4].id == "item4"
        assert blinds[4].name == "WC EG"
        assert blinds[4].position == 100.00
        assert blinds[4].state == BlindState.STOP

        assert blinds[5].id == "item5"
        assert blinds[5].name == "Arbeiten"
        assert blinds[5].position == 100.00
        assert blinds[5].state == BlindState.STOP

        assert blinds[6].id == "item6"
        assert blinds[6].name == "Eltern"
        assert blinds[6].position == 94.96
        assert blinds[6].state == BlindState.DOWN

        assert blinds[7].id == "item7"
        assert blinds[7].name == "Kind 1"
        assert blinds[7].position == 100.00
        assert blinds[7].state == BlindState.STOP

        assert blinds[8].id == "item8"
        assert blinds[8].name == "Kind 2"
        assert blinds[8].position == 100.00
        assert blinds[8].state == BlindState.STOP

        assert blinds[9].id == "item9"
        assert blinds[9].name == "Bad OG"
        assert blinds[9].position == 100.00
        assert blinds[9].state == BlindState.STOP
