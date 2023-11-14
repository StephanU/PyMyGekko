import json
import logging
import pkgutil
from abc import ABC
from abc import abstractmethod

from aiohttp import ClientSession
from yarl import URL


_LOGGER: logging.Logger = logging.getLogger(__name__)


class DataSubscriberInterface:
    def update_status(self, status):
        pass

    def update_resources(self, resource):
        pass


class DataProviderBase(ABC):
    _subscriber: list[DataSubscriberInterface] = []
    _status = None
    _resources = None

    @property
    def resources(self):
        return self._resources

    @resources.setter
    def resources(self, resources):
        self._resources = resources
        for subscriber in self._subscriber:
            subscriber.update_resources(self._resources)

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        self._status = status
        for subscriber in self._subscriber:
            subscriber.update_status(self._status)

    def subscribe(self, subscriber: DataSubscriberInterface):
        self._subscriber.append(subscriber)

    @abstractmethod
    async def read_data(self) -> None:
        ...

    @abstractmethod
    async def write_data(self, resource_path: str, value: str):
        ...


class DummyDataProvider(DataProviderBase):
    async def read_data(self) -> None:
        var_demo_data = pkgutil.get_data(__name__, "api_var_demo_data.json")
        self.resources = json.loads(var_demo_data)

        status_demo_data = pkgutil.get_data(__name__, "api_var_status_demo_data.json")
        self.status = json.loads(status_demo_data)

    async def write_data(self, resource_path: str, value: str):
        _LOGGER.info("Writing to %s %s", resource_path, value)


class DataProvider(DataProviderBase):
    def __init__(
        self, url: URL, authentication_params: dict[str, str], session: ClientSession
    ):
        self._url = url
        self._authentication_params = authentication_params
        self._session = session

    async def read_data(self) -> None:
        _LOGGER.info("read_data /api/v1/var")
        async with self._session.get(
            self._url.with_path("/api/v1/var"),
            params=self._authentication_params,
        ) as resp:
            _LOGGER.info("read_data /api/v1/var response received")
            if resp.status == 200:
                _LOGGER.info(
                    "read_data /api/v1/var response received, 200 %s", resp.text()
                )
                self.resources = await resp.json(content_type="text/plain")
            else:
                _LOGGER.info(
                    "Error reading the resources %s %s", resp.status, resp.text()
                )
                raise Exception

        _LOGGER.info("read_data /api/v1/var/status")
        async with self._session.get(
            self._url.with_path("/api/v1/var/status"),
            params=self._authentication_params,
        ) as resp:
            _LOGGER.info("read_data /api/v1/var/status response received")
            if resp.status == 200:
                _LOGGER.info(
                    "read_data /api/v1/var/status response received, 200, %s".resp.text()
                )
                self.status = await resp.json(content_type="text/plain")
                _LOGGER.info("read_data /api/v1/var/status response received, 200")
            else:
                _LOGGER.info(
                    "Error reading the resources %s %s", resp.status, resp.text()
                )
                raise Exception

        _LOGGER.info("read_data end")

    async def write_data(self, resource_path: str, value: str):
        async with self._session.get(
            self._url.with_path("/api/v1/var/" + resource_path + "/scmd/set"),
            params=self._authentication_params | {"value": value},
        ) as resp:
            _LOGGER.info("write_data %s", resp)
