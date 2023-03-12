import pytest
from decouple import config
from PyMyGekko.PyMyGekko import PyMyGekko


def test_init():
    api = PyMyGekko("username", "apiKey", "gekkoId")

    assert api != None


@pytest.mark.asyncio
async def test_try_connect():
    api = PyMyGekko(config("USERNAME"), config("APIKEY"), config("GEKKOID"))

    response_status = await api.try_connect()
    assert response_status == 200


@pytest.mark.asyncio
async def test_get_globals_network():
    api = PyMyGekko(config("USERNAME"), config("APIKEY"), config("GEKKOID"))

    await api.read_data()
    globals_network = api.get_globals_network()

    assert globals_network != None
    print(globals_network)
