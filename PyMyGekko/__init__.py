# SPDX-FileCopyrightText: 2023-present Stephan Uhle <stephanu@gmx.net>
#
# SPDX-License-Identifier: MIT
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

    async def try_connect(self) -> int:
        if self._demo_mode:
            return 200
        else:
            async with self._session.get(
                self._url.with_path("/api/v1/var"), params=self._authentication_params
            ) as resp:
                return resp.status

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
