import aiohttp
from yarl import URL


class PyMyGekko:
    def __init__(
        self,
        username: str,
        apiKey: str,
        gekkoId: str,
        scheme: str = "https",
        host: str = "live.my-gekko.com",
        port: int = None,
    ) -> None:
        self._url = URL.build(scheme=scheme, host=host, port=port)
        self._authentication_params = {
            "username": username,
            "key": apiKey,
            "gekkoid": gekkoId,
        }

    async def try_connect(self) -> int:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                self._url.with_path("/api/v1/var"), params=self._authentication_params
            ) as resp:
                return resp.status

    async def read_data(self) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                self._url.with_path("/api/v1/var/status"),
                params=self._authentication_params,
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
