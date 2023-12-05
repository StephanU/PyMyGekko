"""Base implementation of the data provider"""
import json
import logging
import pkgutil
from abc import ABC
from abc import abstractmethod

from aiohttp import ClientSession
from yarl import URL

from .resources import Entity

_LOGGER: logging.Logger = logging.getLogger(__name__)


class DataSubscriberInterface:
    """Interface for data subscribers"""

    def update_status(self, status):
        """Method called on status updates"""

    def update_resources(self, resources):
        """Method called on resources updates"""


class EntityValueAccessor(DataSubscriberInterface):
    """Base class for entity values accessors"""

    _data = {}

    def get_value(self, entity: Entity, value_name: str) -> str | None:
        """Returns a data value of this entity"""
        if entity and entity.entity_id:
            if (
                entity.entity_id in self._data
                and value_name in self._data[entity.entity_id]
                and self._data[entity.entity_id][value_name]
            ):
                return self._data[entity.entity_id][value_name]
        return None


class DataProviderBase(ABC):
    """Base class for data providers"""

    _subscriber: list[DataSubscriberInterface] = []
    _status = None
    _resources = None

    @property
    def resources(self):
        """returns the read resources"""
        return self._resources

    @resources.setter
    def resources(self, resources):
        self._resources = resources
        for subscriber in self._subscriber:
            subscriber.update_resources(self._resources)

    @property
    def status(self):
        """returns the read status"""
        return self._status

    @status.setter
    def status(self, status):
        self._status = status
        for subscriber in self._subscriber:
            subscriber.update_status(self._status)

    def subscribe(self, subscriber: DataSubscriberInterface):
        """Method to subscribe to data changes."""
        self._subscriber.append(subscriber)

    @abstractmethod
    async def read_data(self) -> None:
        """Reads data from the MyGekko API"""

    @abstractmethod
    async def write_data(self, resource_path: str, value: str):
        """Sends data to the MyGekko API"""


class DummyDataProvider(DataProviderBase):
    """Dummy data provider returning static test data"""

    async def read_data(self) -> None:
        var_demo_data = pkgutil.get_data(__name__, "api_var_demo_data.json")
        self.resources = json.loads(var_demo_data)

        status_demo_data = pkgutil.get_data(__name__, "api_var_status_demo_data.json")
        self.status = json.loads(status_demo_data)

    async def write_data(self, resource_path: str, value: str):
        _LOGGER.info("Writing to %s %s", resource_path, value)


class DataProvider(DataProviderBase):
    """Data provider accessing the MyGekko API"""

    def __init__(
        self, url: URL, authentication_params: dict[str, str], session: ClientSession
    ):
        self._url = url
        self._authentication_params = authentication_params
        self._session = session

    async def read_data(self) -> None:
        _LOGGER.debug("read_data /api/v1/var")
        async with self._session.get(
            self._url.with_path("/api/v1/var"),
            params=self._authentication_params,
        ) as resp:
            if resp.status == 200:
                response_text = await resp.text()
                try:
                    self.resources = json.loads(response_text)
                except Exception:
                    _LOGGER.exception("Json Parsing the response failed")
            else:
                _LOGGER.error(
                    "Error reading the resources %s %s", resp.status, await resp.text()
                )
                raise Exception

        _LOGGER.debug("read_data /api/v1/var/status")
        async with self._session.get(
            self._url.with_path("/api/v1/var/status"),
            params=self._authentication_params,
        ) as resp:
            if resp.status == 200:
                response_text = await resp.text()
                try:
                    self.status = json.loads(response_text)
                except Exception:
                    _LOGGER.exception("Json Parsing the response failed")
            else:
                _LOGGER.error(
                    "Error reading the resources %s %s", resp.status, await resp.text()
                )
                raise Exception

        _LOGGER.debug("read_data end")

    async def write_data(self, resource_path: str, value: str):
        resource_url = "/api/v1/var" + resource_path + "/scmd/set"

        _LOGGER.debug("Writing data %s to %s", value, resource_url)

        async with self._session.get(
            self._url.with_path(resource_url),
            params=self._authentication_params | {"value": value},
        ) as resp:
            _LOGGER.debug("write_data %s", resp)
