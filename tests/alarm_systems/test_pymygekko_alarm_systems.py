import pytest
from aiohttp import ClientSession
from aiohttp import web
from PyMyGekko import MyGekkoApiClientBase
from PyMyGekko.resources.AlarmSystems import AlarmSystemAlarmState
from PyMyGekko.resources.AlarmSystems import AlarmSystemDeviceModel
from PyMyGekko.resources.AlarmSystems import AlarmSystemDeviceState
from PyMyGekko.resources.AlarmSystems import AlarmSystemFeature
from PyMyGekko.resources.AlarmSystems import AlarmSystemSharpState


async def var_response(request):
    varResponseFile = open("tests/alarm_systems/data/api_var_response.json")
    return web.Response(status=200, body=varResponseFile.read())


async def var_status_response(request):
    statusResponseFile = open("tests/alarm_systems/data/api_var_status_response.json")
    return web.Response(status=200, body=statusResponseFile.read())


@pytest.fixture
def mock_server(aiohttp_server):
    app = web.Application()
    app.router.add_get("/api/v1/var", var_response)
    app.router.add_get("/api/v1/var/status", var_status_response)
    return aiohttp_server(app)


async def _read_api(server, session):
    api = MyGekkoApiClientBase(
        {},
        session,
        scheme=server.scheme,
        host=server.host,
        port=server.port,
    )
    await api.read_data()
    return api


@pytest.mark.asyncio
async def test_get_alarm_systems(mock_server):
    server = await mock_server
    async with ClientSession() as session:
        api = await _read_api(server, session)
        alarm_systems = api.get_alarm_systems()

        assert len(alarm_systems) == 8

        ground_floor = alarm_systems[0]
        assert ground_floor.entity_id == "item0"
        assert ground_floor.name == "SB1 EG"
        assert ground_floor.resource_path == "/alarmsystem/item0"
        assert ground_floor.alarm_state == AlarmSystemAlarmState.OK
        assert ground_floor.sharp_state == AlarmSystemSharpState.UNSHARP
        assert ground_floor.device_model == AlarmSystemDeviceModel.HIPLEX8400_V2
        assert ground_floor.device_state == AlarmSystemDeviceState.FAULT
        assert ground_floor.active_input_groups == [0, 5, 379]
        assert ground_floor.input_group_count == 512
        assert ground_floor.supported_features == [
            AlarmSystemFeature.ARM_INTERNAL,
            AlarmSystemFeature.ARM_EXTERNAL,
        ]

        assert alarm_systems[1].sharp_state == AlarmSystemSharpState.EXTERNAL_SHARP
        assert alarm_systems[3].sharp_state == AlarmSystemSharpState.INTERNAL_SHARP
        assert alarm_systems[4].alarm_state == AlarmSystemAlarmState.ALARM
        assert alarm_systems[5].sharp_state == AlarmSystemSharpState.NO_INFO
        assert alarm_systems[7].name == "SB8 Tresor-Lager"


@pytest.mark.asyncio
async def test_unknown_and_malformed_values(mock_server):
    server = await mock_server
    async with ClientSession() as session:
        api = await _read_api(server, session)
        status = api._data_provider.status
        status["alarmsystem"]["item0"]["sumstate"]["value"] = "7;9;8;nothex;5;;;"
        api._data_provider.status = status

        ground_floor = api.get_alarm_systems()[0]
        assert ground_floor.alarm_state is None
        assert ground_floor.device_model is None
        assert ground_floor.sharp_state is None
        assert ground_floor.device_state is None
        assert ground_floor.active_input_groups is None


@pytest.mark.asyncio
async def test_set_sharp_state(mock_server):
    server = await mock_server
    async with ClientSession() as session:
        api = await _read_api(server, session)
        alarm_system = api.get_alarm_systems()[2]

        written = {}

        async def fake_write(resource_path, value):
            written["resource_path"] = resource_path
            written["value"] = value

        api._data_provider.write_data = fake_write

        await alarm_system.set_sharp_state(AlarmSystemSharpState.EXTERNAL_SHARP)
        assert written == {"resource_path": "/alarmsystem/item2", "value": "3"}

        await alarm_system.set_sharp_state(AlarmSystemSharpState.INTERNAL_SHARP)
        assert written == {"resource_path": "/alarmsystem/item2", "value": "2"}


@pytest.mark.asyncio
async def test_set_sharp_state_rejects_commands_the_item_does_not_accept(mock_server):
    server = await mock_server
    async with ClientSession() as session:
        api = await _read_api(server, session)
        alarm_system = api.get_alarm_systems()[0]

        async def fake_write(resource_path, value):
            raise AssertionError("must not be written")

        api._data_provider.write_data = fake_write

        with pytest.raises(ValueError):
            await alarm_system.set_sharp_state(AlarmSystemSharpState.UNSHARP)
        with pytest.raises(ValueError):
            await alarm_system.set_sharp_state(AlarmSystemSharpState.NO_INFO)


@pytest.mark.asyncio
async def test_disarm_supported_when_announced(mock_server):
    server = await mock_server
    async with ClientSession() as session:
        api = MyGekkoApiClientBase(
            {}, session, scheme=server.scheme, host=server.host, port=server.port
        )
        await api.read_data()
        resources = api._data_provider.resources
        resources["alarmsystem"]["item0"]["scmd"][
            "value"
        ] = "1|2|3 (Unsharp|Internal|External)"
        api._data_provider.resources = resources

        assert api.get_alarm_systems()[0].supported_features == [
            AlarmSystemFeature.DISARM,
            AlarmSystemFeature.ARM_INTERNAL,
            AlarmSystemFeature.ARM_EXTERNAL,
        ]


@pytest.mark.asyncio
async def test_no_alarm_system(aiohttp_server):
    async def var(request):
        return web.Response(
            status=200, body=open("tests/clocks/data/api_var_response.json").read()
        )

    async def var_status(request):
        return web.Response(
            status=200,
            body=open("tests/clocks/data/api_var_status_response.json").read(),
        )

    app = web.Application()
    app.router.add_get("/api/v1/var", var)
    app.router.add_get("/api/v1/var/status", var_status)
    server = await aiohttp_server(app)
    async with ClientSession() as session:
        api = await _read_api(server, session)
        assert api.get_alarm_systems() == []
