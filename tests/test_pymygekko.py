import logging
import traceback

import pytest
from aiohttp import ClientSession
from aiohttp import ConnectionTimeoutError
from aiohttp import web
from PyMyGekko import MyGekkoApiClientBase
from PyMyGekko import MyGekkoLocalApiClient
from PyMyGekko.data_provider import MyGekkoConnectionError


async def response(request):
    return web.Response(status=200)


@pytest.fixture
def mock_server(aiohttp_server):
    app = web.Application()
    app.router.add_get("/api/v1/var", response)
    return aiohttp_server(app)


@pytest.mark.asyncio
async def test_init():
    async with ClientSession() as session:
        api = MyGekkoApiClientBase("username", "apiKey", "gekkoId", session)

        assert api is not None


@pytest.mark.asyncio
async def test_try_connect(mock_server):
    server = await mock_server
    async with ClientSession() as session:
        api = MyGekkoApiClientBase(
            {},
            session,
            scheme=server.scheme,
            host=server.host,
            port=server.port,
        )

        await api.try_connect()


@pytest.mark.asyncio
async def test_read_data_reads_resources_only_once(aiohttp_server):
    request_count = {"var": 0, "status": 0}

    async def var_response(request):
        request_count["var"] += 1
        return web.Response(status=200, body='{"globals": {"network": {}}}')

    async def var_status_response(request):
        request_count["status"] += 1
        return web.Response(status=200, body='{"globals": {"network": {}}}')

    app = web.Application()
    app.router.add_get("/api/v1/var", var_response)
    app.router.add_get("/api/v1/var/status", var_status_response)
    server = await aiohttp_server(app)

    async with ClientSession() as session:
        api = MyGekkoApiClientBase(
            {},
            session,
            scheme=server.scheme,
            host=server.host,
            port=server.port,
        )

        await api.read_data()
        await api.read_data()

        assert request_count["var"] == 1
        assert request_count["status"] == 2


class _TimingOutSession:
    """Session whose requests fail like aiohttp's connection timeout.

    aiohttp puts the full request URL, including the query string with the
    credentials, into the message of ConnectionTimeoutError.
    """

    def get(self, url, params=None):
        raise ConnectionTimeoutError(
            f"Connection timeout to host {url.with_query(params)}"
        )


async def _call_api(api, method):
    if method == "write_data":
        # Entities write through the data provider, the client has no write method.
        await api._data_provider.write_data("/lights/item0", "1")
    else:
        await getattr(api, method)()


@pytest.mark.asyncio
@pytest.mark.parametrize("method", ["try_connect", "read_data", "write_data"])
async def test_connection_timeout_does_not_expose_credentials(method, caplog):
    caplog.set_level(logging.DEBUG)
    api = MyGekkoLocalApiClient(
        "the-user", "the-password", _TimingOutSession(), "192.0.2.1"
    )

    with pytest.raises(MyGekkoConnectionError) as exc_info:
        await _call_api(api, method)

    formatted = "".join(traceback.format_exception(exc_info.value))
    assert "ConnectionTimeoutError" in str(exc_info.value)
    assert "192.0.2.1" in str(exc_info.value)
    for secret in ("the-user", "the-password"):
        assert secret not in formatted
        assert secret not in caplog.text


@pytest.mark.asyncio
@pytest.mark.parametrize("method", ["try_connect", "read_data", "write_data"])
async def test_connection_error_does_not_expose_credentials(
    method, unused_tcp_port, caplog
):
    caplog.set_level(logging.DEBUG)
    async with ClientSession() as session:
        api = MyGekkoApiClientBase(
            {"username": "the-user", "password": "the-password"},
            session,
            scheme="http",
            host="127.0.0.1",
            port=unused_tcp_port,
        )

        with pytest.raises(MyGekkoConnectionError) as exc_info:
            await _call_api(api, method)

    formatted = "".join(traceback.format_exception(exc_info.value))
    assert "/api/v1/var" in str(exc_info.value)
    for secret in ("the-user", "the-password"):
        assert secret not in formatted
        assert secret not in caplog.text
