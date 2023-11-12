# SPDX-FileCopyrightText: 2023-present Stephan Uhle <stephanu@gmx.net>
#
# SPDX-License-Identifier: MIT
import logging

from aiohttp import ClientSession
from PyMyGekko.resources.Blinds import Blind
from PyMyGekko.resources.Blinds import BlindValueAccessor
from PyMyGekko.resources.EnergyMeters import EnergyMeter
from PyMyGekko.resources.EnergyMeters import EnergyMeterValueAccessor
from PyMyGekko.resources.Lights import Light
from PyMyGekko.resources.Lights import LightValueAccessor
from PyMyGekko.resources.Thermostats import Thermostat
from PyMyGekko.resources.Thermostats import ThermostatValueAccessor
from yarl import URL

from .DataProvider import DataProvider
from .DataProvider import DummyDataProvider


_LOGGER: logging.Logger = logging.getLogger(__package__)


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

        self._blind_value_accessor = BlindValueAccessor(self._data_provider)
        self._light_value_accessor = LightValueAccessor(self._data_provider)
        self._thermostat_value_accessor = ThermostatValueAccessor(self._data_provider)
        self._energy_meter_value_accessor = EnergyMeterValueAccessor(
            self._data_provider
        )

    async def try_connect(self) -> None:
        _LOGGER.info("try_connect")
        if self._demo_mode:
            pass
        else:
            async with self._session.get(
                self._url.with_path("/api/v1/var"), params=self._authentication_params
            ) as resp:
                if resp.status == 200:
                    _LOGGER.info("Ok", resp)
                    pass
                elif resp.status == 400:
                    _LOGGER.info("MyGekkoBadRequest", resp)
                    raise MyGekkoBadRequest()
                elif resp.status == 403:
                    _LOGGER.info("MyGekkoForbidden", resp)
                    raise MyGekkoForbidden()
                elif resp.status == 404:
                    _LOGGER.info("MyGekkoNotFound", resp)
                    raise MyGekkoNotFound()
                elif resp.status == 405:
                    _LOGGER.info("MyGekkoMethodNotAllowed", resp)
                    raise MyGekkoMethodNotAllowed()
                elif resp.status == 410:
                    _LOGGER.info("MyGekkoGone", resp)
                    raise MyGekkoGone()
                elif resp.status == 429:
                    _LOGGER.info("MyGekkoTooManyRequests", resp)
                    raise MyGekkoTooManyRequests()
                elif resp.status == 444:
                    _LOGGER.info("MyGekkoNoResponse", resp)
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

    def get_blinds(self) -> list[Blind]:
        return self._blind_value_accessor.blinds

    def get_lights(self) -> list[Light]:
        return self._light_value_accessor.lights

    def get_thermostats(self) -> list[Thermostat]:
        return self._thermostat_value_accessor.thermostats

    def get_energy_meters(self) -> list[EnergyMeter]:
        return self._energy_meter_value_accessor.energyMeters


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
