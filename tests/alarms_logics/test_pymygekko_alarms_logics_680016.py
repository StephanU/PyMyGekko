import pytest
from aiohttp import ClientSession
from aiohttp import web
from PyMyGekko import MyGekkoApiClient


async def var_response(request):
    varResponseFile = open("tests/alarms_logics/data/api_var_response_680016.json")
    return web.Response(status=200, body=varResponseFile.read())


async def var_status_response(request):
    statusResponseFile = open(
        "tests/alarms_logics/data/api_var_status_response_680016.json"
    )
    return web.Response(status=200, body=statusResponseFile.read())


@pytest.fixture
def mock_server(aiohttp_server):
    app = web.Application()
    app.router.add_get("/api/v1/var", var_response)
    app.router.add_get("/api/v1/var/status", var_status_response)
    return aiohttp_server(app)


@pytest.mark.asyncio
async def test_get_alarms_logics(mock_server):
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
        alarms_logics = api.get_alarms_logics()

        assert alarms_logics is not None
        assert len(alarms_logics) == 11

        assert alarms_logics[0].id == "item0"
        assert alarms_logics[0].name == "Wasserbruchsensor"
        assert alarms_logics[0].value == 0.0

        assert alarms_logics[1].id == "item1"
        assert alarms_logics[1].name == "Rauchmelder"
        assert alarms_logics[1].value == 1.0

        assert alarms_logics[2].id == "item2"
        assert alarms_logics[2].name == "Klingel"
        assert alarms_logics[2].value == 0.0

        assert alarms_logics[3].id == "item3"
        assert alarms_logics[3].name == "Licht BW dimmen bei Nacht"
        assert alarms_logics[3].value == 0.0

        assert alarms_logics[4].id == "item4"
        assert alarms_logics[4].name == "Lüftung aus bei VOC Grenz"
        assert alarms_logics[4].value == 0.0

        assert alarms_logics[5].id == "item5"
        assert alarms_logics[5].name == "LED Taster immer an"
        assert alarms_logics[5].value == 1.0

        assert alarms_logics[6].id == "item6"
        assert alarms_logics[6].name == "Hue OG Flurschrank dimmen"
        assert alarms_logics[6].value == 255.0

        assert alarms_logics[7].id == "item7"
        assert alarms_logics[7].name == "Aussen Dämmerung"
        assert alarms_logics[7].value == 0.0

        assert alarms_logics[8].id == "item8"
        assert alarms_logics[8].name == "BW OG"
        assert alarms_logics[8].value == 0.0

        assert alarms_logics[9].id == "item9"
        assert alarms_logics[9].name == "Runter bei Dämmerung "
        assert alarms_logics[9].value == 0.0

        assert alarms_logics[10].id == "item10"
        assert alarms_logics[10].name == "Test"
        assert alarms_logics[10].value == 1.0
