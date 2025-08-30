from aiohttp import ClientSession
from aiohttp import web
from PyMyGekko import MyGekkoApiClientBase
from pytest import fixture
from pytest import mark


async def var_response(request):
    varResponseFile = open("tests/meteo/api_var_response_879015.json")
    return web.Response(status=200, body=varResponseFile.read())


async def var_status_response(request):
    statusResponseFile = open("tests/meteo/api_var_status_response_879015.json")
    return web.Response(status=200, body=statusResponseFile.read())


@fixture
def mock_server(aiohttp_server):
    app = web.Application()
    app.router.add_get("/api/v1/var", var_response)
    app.router.add_get("/api/v1/var/status", var_status_response)
    return aiohttp_server(app)


@mark.asyncio
async def test_get_meteo(mock_server):
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
        meteo = api.get_meteo()

        assert meteo is not None
        assert meteo.sensor_data["twilight"] == "10000.000000"
        assert meteo.sensor_data["brightness"] == "99.000000"
        assert meteo.sensor_data["brightnessw"] == "21.000000"
        assert meteo.sensor_data["brightnesso"] == "16.000000"
        assert meteo.sensor_data["wind"] == "0.003052"
        assert meteo.sensor_data["temperature"] == "23.400000"
        assert meteo.sensor_data["rain"] == "0.000000"
