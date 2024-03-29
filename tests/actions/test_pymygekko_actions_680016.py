import pytest
from aiohttp import ClientSession
from aiohttp import web
from PyMyGekko import MyGekkoApiClientBase
from PyMyGekko.resources.Actions import ActionFeature
from PyMyGekko.resources.Actions import ActionState


async def var_response(request):
    varResponseFile = open("tests/actions/data/api_var_response_680016.json")
    return web.Response(status=200, body=varResponseFile.read())


async def var_status_response(request):
    statusResponseFile = open("tests/actions/data/api_var_status_response_680016.json")
    return web.Response(status=200, body=statusResponseFile.read())


@pytest.fixture
def mock_server(aiohttp_server):
    app = web.Application()
    app.router.add_get("/api/v1/var", var_response)
    app.router.add_get("/api/v1/var/status", var_status_response)
    return aiohttp_server(app)


@pytest.mark.asyncio
async def test_get_actions(mock_server):
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
        actions = api.get_actions()

        assert actions is not None
        assert len(actions) == 4

        assert actions[0].entity_id == "item0"
        assert actions[0].name == "Zentral AUS"
        assert actions[0].state == ActionState.OFF
        assert len(actions[0].supported_features) == 1
        assert ActionFeature.ON_OFF in actions[0].supported_features

        assert actions[1].entity_id == "item1"
        assert actions[1].name == "Alle runter"
        assert actions[1].state == ActionState.OFF
        assert len(actions[1].supported_features) == 1
        assert ActionFeature.ON_OFF in actions[1].supported_features

        assert actions[2].entity_id == "item2"
        assert actions[2].name == "Alle auf Komfort"
        assert actions[2].state == ActionState.OFF
        assert len(actions[2].supported_features) == 1
        assert ActionFeature.ON_OFF in actions[2].supported_features
