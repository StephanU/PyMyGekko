from aiohttp import ClientSession
from yarl import URL

from PyMyGekko.resources import Blinds


class PyMyGekkoApiClient:
    def __init__(
        self,
        username: str,
        apiKey: str,
        gekkoId: str,
        session: ClientSession,
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
        self._session = session

    async def try_connect(self) -> int:
        async with self._session.get(
            self._url.with_path("/api/v1/var"), params=self._authentication_params
        ) as resp:
            return resp.status

    async def read_data(self) -> None:
        async with self._session.get(
            self._url.with_path("/api/v1/var"),
            params=self._authentication_params,
        ) as resp:
            self._resources = await resp.json(content_type="text/plain")
        async with self._session.get(
            self._url.with_path("/api/v1/var/status"),
            params=self._authentication_params,
        ) as resp:
            self._status = await resp.json(content_type="text/plain")

    def get_globals_network(self):
        if self._status == None:
            return None

        result = {}
        if self._status["globals"] and self._status["globals"]["network"]:
            network_data = self._status["globals"]["network"]
            for key in network_data:
                result[key] = network_data[key]["value"]

        return result

    def get_blinds(self) -> list[Blinds] | None:
        if self._resources == None:
            return None

        result: list[Blinds] = []
        if self._resources["blinds"]:
            blinds = self._resources["blinds"]
            for key in blinds:
                if key.startswith("item"):
                    result.append(Blinds(key, blinds[key]["name"]))

        return result
