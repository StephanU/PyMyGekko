import json
import pkgutil

from typing import Any
from aiohttp import ClientSession
from yarl import URL

from .DataProvider import DataProvider
from PyMyGekko.resources.Blinds import Blind, BlindValueAccessor


class MyGekkoApiClient:
    def __init__(
        self,
        username: str,
        apiKey: str,
        gekkoId: str,
        session: ClientSession,
        demo_mode: bool = False,
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
        self._demo_mode = demo_mode
        self._data_provider = DataProvider()
        self._blind_value_accessor = BlindValueAccessor(self._data_provider)

    async def try_connect(self) -> int:
        if self._demo_mode:
            return 200
        else:
            async with self._session.get(
                self._url.with_path("/api/v1/var"), params=self._authentication_params
            ) as resp:
                return resp.status

    async def read_data(self) -> None:
        if self._demo_mode:
            var_demo_data = pkgutil.get_data(__name__, "api_var_demo_data.json")
            self._data_provider.resources = json.loads(var_demo_data)

            status_demo_data = pkgutil.get_data(
                __name__, "api_var_status_demo_data.json"
            )
            self._data_provider.status = json.loads(status_demo_data)
            return
        else:
            async with self._session.get(
                self._url.with_path("/api/v1/var"),
                params=self._authentication_params,
            ) as resp:
                self._data_provider.resources = await resp.json(
                    content_type="text/plain"
                )

            async with self._session.get(
                self._url.with_path("/api/v1/var/status"),
                params=self._authentication_params,
            ) as resp:
                self._data_provider.status = await resp.json(content_type="text/plain")

    def get_globals_network(self):
        if self._data_provider.status == None:
            return None

        result = {}
        if (
            self._data_provider.status["globals"]
            and self._data_provider.status["globals"]["network"]
        ):
            network_data = self._data_provider.status["globals"]["network"]
            for key in network_data:
                result[key] = network_data[key]["value"]

        return result

    def get_blinds(self) -> list[Blind]:
        return self._blind_value_accessor.blinds
