# SPDX-FileCopyrightText: 2023-present Stephan Uhle <stephanu@gmx.net>
#
# SPDX-License-Identifier: MIT
import logging

from aiohttp import ClientSession
from PyMyGekko.resources.Actions import Action
from PyMyGekko.resources.Actions import ActionValueAccessor
from PyMyGekko.resources.AlarmsLogics import AlarmsLogicValueAccessor
from PyMyGekko.resources.Blinds import Blind
from PyMyGekko.resources.Blinds import BlindValueAccessor
from PyMyGekko.resources.EnergyCosts import EnergyCost
from PyMyGekko.resources.EnergyCosts import EnergyCostValueAccessor
from PyMyGekko.resources.HotWaterSystems import HotWaterSystem
from PyMyGekko.resources.HotWaterSystems import HotWaterSystemValueAccessor
from PyMyGekko.resources.Lights import Light
from PyMyGekko.resources.Lights import LightValueAccessor
from PyMyGekko.resources.Loads import Load
from PyMyGekko.resources.Loads import LoadValueAccessor
from PyMyGekko.resources.RoomTemps import RoomTemp
from PyMyGekko.resources.RoomTemps import RoomTempsValueAccessor
from PyMyGekko.resources.vents import Vent
from PyMyGekko.resources.vents import VentValueAccessor
from yarl import URL

from .data_provider import DataProvider
from .data_provider import DummyDataProvider


_LOGGER: logging.Logger = logging.getLogger(__name__)


class MyGekkoApiClientBase:
    """The base class for the MyGekko api client"""

    def __init__(
        self,
        authentication_params: dict,
        session: ClientSession,
        demo_mode: bool = False,
        scheme: str = "https",
        host: str = "live.my-gekko.com",
        port: int = None,
    ) -> None:
        self._url = URL.build(scheme=scheme, host=host, port=port)
        self._authentication_params = authentication_params
        self._session = session
        self._demo_mode = demo_mode

        if self._demo_mode:
            self._data_provider = DummyDataProvider()
        else:
            self._data_provider = DataProvider(
                self._url, self._authentication_params, self._session
            )

        self._actions_value_accessor = ActionValueAccessor(self._data_provider)
        self._alarm_logics_value_accessor = AlarmsLogicValueAccessor(
            self._data_provider
        )
        self._blind_value_accessor = BlindValueAccessor(self._data_provider)
        self._energy_costs_value_accessor = EnergyCostValueAccessor(self._data_provider)
        self._hot_water_systems_value_accessor = HotWaterSystemValueAccessor(
            self._data_provider
        )
        self._light_value_accessor = LightValueAccessor(self._data_provider)
        self._loads_value_accessor = LoadValueAccessor(self._data_provider)
        self._room_temps_value_accessor = RoomTempsValueAccessor(self._data_provider)
        self._vents_value_accessor = VentValueAccessor(self._data_provider)

    async def try_connect(self) -> None:
        """Tries to connect to the MyGekko API using the given credentials"""
        _LOGGER.debug("try_connect")
        if self._demo_mode:
            pass
        else:
            async with self._session.get(
                self._url.with_path("/api/v1/var"), params=self._authentication_params
            ) as resp:
                response_text = await resp.text()
                if resp.status == 200:
                    _LOGGER.debug("Ok %s", response_text)
                elif resp.status == 400:
                    _LOGGER.error("MyGekkoBadRequest %s", response_text)
                    raise MyGekkoBadRequest()
                elif resp.status == 403:
                    _LOGGER.error("MyGekkoForbidden %s", response_text)
                    raise MyGekkoForbidden()
                elif resp.status == 404:
                    _LOGGER.error("MyGekkoNotFound %s", response_text)
                    raise MyGekkoNotFound()
                elif resp.status == 405:
                    _LOGGER.error("MyGekkoMethodNotAllowed %s", response_text)
                    raise MyGekkoMethodNotAllowed()
                elif resp.status == 410:
                    _LOGGER.error("MyGekkoGone %s", response_text)
                    raise MyGekkoGone()
                elif resp.status == 429:
                    _LOGGER.error("MyGekkoTooManyRequests %s", response_text)
                    raise MyGekkoTooManyRequests()
                elif resp.status == 444:
                    _LOGGER.error("MyGekkoNoResponse %s", response_text)
                    raise MyGekkoNoResponse()
                else:
                    raise MyGekkoError()

    async def read_data(self) -> None:
        """Reads the status and resources data via the MyGekko API"""
        await self._data_provider.read_data()

    def get_globals_network(self):
        """Returns the globals network information"""
        if self._data_provider.status is None:
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

    def get_actions(self) -> list[Action]:
        """Returns the MyGekko actions"""
        return self._actions_value_accessor.actions

    def get_alarms_logics(self) -> list[Action]:
        """Returns the MyGekko alarms_logics"""
        return self._alarm_logics_value_accessor.alarms_logics

    def get_blinds(self) -> list[Blind]:
        """Returns the MyGekko blinds"""
        return self._blind_value_accessor.blinds

    def get_energy_costs(self) -> list[EnergyCost]:
        """Returns the MyGekko energy_costs"""
        return self._energy_costs_value_accessor.energy_costs

    def get_hot_water_systems(self) -> list[HotWaterSystem]:
        """Returns the MyGekko hot_water_systens"""
        return self._hot_water_systems_value_accessor.hotwater_systems

    def get_lights(self) -> list[Light]:
        """Returns the MyGekko lights"""
        return self._light_value_accessor.lights

    def get_loads(self) -> list[Load]:
        """Returns the MyGekko load"""
        return self._loads_value_accessor.loads

    def get_room_temps(self) -> list[RoomTemp]:
        """Returns the MyGekko room_temps"""
        return self._room_temps_value_accessor.room_temps

    def get_vents(self) -> list[Vent]:
        """Returns the MyGekko vents"""
        return self._vents_value_accessor.vents


class MyGekkoQueryApiClient(MyGekkoApiClientBase):
    """The api client to access MyGekko via the MyGekko query api"""

    def __init__(
        self,
        username: str,
        api_key: str,
        gekko_id: str,
        session: ClientSession,
    ) -> None:
        super().__init__(
            {
                "username": username,
                "key": api_key,
                "gekkoid": gekko_id,
            },
            session,
        )


class MyGekkoLocalApiClient(MyGekkoApiClientBase):
    """The api client to access MyGekko locally."""

    def __init__(
        self,
        username: str,
        password: str,
        session: ClientSession,
        host: str,
    ) -> None:
        super().__init__(
            {
                "username": username,
                "password": password,
            },
            session,
            host,
        )


class MyGekkoError(Exception):
    """Base MyGekko exception."""


class MyGekkoBadRequest(MyGekkoError):
    """MyGekko Bad Request exception."""


class MyGekkoForbidden(MyGekkoError):
    """MyGekko Forbidden exception."""


class MyGekkoNotFound(MyGekkoError):
    """MyGekko Not Found exception."""


class MyGekkoMethodNotAllowed(MyGekkoError):
    """MyGekko Method Not Allowed exception."""


class MyGekkoGone(MyGekkoError):
    """MyGekko Gone exception."""


class MyGekkoTooManyRequests(MyGekkoError):
    """MyGekko Too Many Requests exception."""


class MyGekkoNoResponse(MyGekkoError):
    """MyGekko No Response exception."""
