import aiohttp


class PyMyGekko:
    def __init__(self, username: str, apiKey: str, gekkoId: str) -> None:
        self._url = "https://live.my-gekko.com/api/v1/var"
        self._authentication_params = {
            "username": username,
            "key": apiKey,
            "gekkoid": gekkoId,
        }

    async def try_connect(self) -> int:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                self._url, params=self._authentication_params
            ) as resp:
                print(resp.status)
                print(await resp.text())
                return resp.status

    async def read_data(self) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                self._url + "/status", params=self._authentication_params
            ) as resp:
                self._data = await resp.json(content_type="text/plain")

    def get_globals_network(self):
        if self._data == None:
            return None

        result = {}
        if self._data["globals"] and self._data["globals"]["network"]:
            network_data = self._data["globals"]["network"]
            for key in network_data:
                result[key] = network_data[key]["value"]

        return result
