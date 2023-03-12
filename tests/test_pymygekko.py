from PyMyGekko.PyMyGekko import PyMyGekko


def test_init():
    api = PyMyGekko("username", "apiKey", "gekkoId")

    assert api != None

