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
from yarl import URL

from .DataProvider import DataProvider
from .DataProvider import DummyDataProvider


_LOGGER: logging.Logger = logging.getLogger(__name__)


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

    async def try_connect(self) -> None:
        _LOGGER.debug("try_connect")
        if self._demo_mode:
            pass
        else:
            async with self._session.get(
                self._url.with_path("/api/v1/var"), params=self._authentication_params
            ) as resp:
                responseText = await resp.text()
                if resp.status == 200:
                    _LOGGER.debug("Ok %s", responseText)
                    pass
                elif resp.status == 400:
                    _LOGGER.error("MyGekkoBadRequest %s", responseText)
                    raise MyGekkoBadRequest()
                elif resp.status == 403:
                    _LOGGER.error("MyGekkoForbidden %s", responseText)
                    raise MyGekkoForbidden()
                elif resp.status == 404:
                    _LOGGER.error("MyGekkoNotFound %s", responseText)
                    raise MyGekkoNotFound()
                elif resp.status == 405:
                    _LOGGER.error("MyGekkoMethodNotAllowed %s", responseText)
                    raise MyGekkoMethodNotAllowed()
                elif resp.status == 410:
                    _LOGGER.error("MyGekkoGone %s", responseText)
                    raise MyGekkoGone()
                elif resp.status == 429:
                    _LOGGER.error("MyGekkoTooManyRequests %s", responseText)
                    raise MyGekkoTooManyRequests()
                elif resp.status == 444:
                    _LOGGER.error("MyGekkoNoResponse %s", responseText)
                    raise MyGekkoNoResponse()
                else:
                    raise MyGekkoError()

    async def read_data(self) -> None:
        await self._data_provider.read_data()

    def get_globals_network(self):
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
        return self._actions_value_accessor.actions

    def get_alarms_logics(self) -> list[Action]:
        return self._alarm_logics_value_accessor.alarmsLogics

    def get_blinds(self) -> list[Blind]:
        return self._blind_value_accessor.blinds

    def get_energy_costs(self) -> list[EnergyCost]:
        return self._energy_costs_value_accessor.energyCosts

    def get_hot_water_systems(self) -> list[HotWaterSystem]:
        return self._hot_water_systems_value_accessor.hotWaterSystems

    def get_lights(self) -> list[Light]:
        return self._light_value_accessor.lights

    def get_loads(self) -> list[Load]:
        return self._loads_value_accessor.loads

    def get_room_temps(self) -> list[RoomTemp]:
        return self._room_temps_value_accessor.roomTemps


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
