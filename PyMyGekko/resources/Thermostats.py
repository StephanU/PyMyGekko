from __future__ import annotations

from enum import IntEnum

from PyMyGekko import DataProvider
from PyMyGekko.resources import Entity


class Thermostat(Entity):
    def __init__(
        self, id: str, name: str, value_accessor: ThermostatValueAccessor
    ) -> None:
        super().__init__(id, name)
        self._value_accessor = value_accessor
        self._resource_path = "/roomtemps/" + self.id
        self._supported_features = self._value_accessor.get_features(self)

    @property
    def resource_path(self) -> str:
        return self._resource_path

    @property
    def supported_features(self) -> list[ThermostatFeature]:
        return self._supported_features

    @property
    def mode(self) -> ThermostatMode | None:
        return self._value_accessor.get_mode(self)

    async def set_mode(self, mode: ThermostatMode):
        await self._value_accessor.set_mode(self, mode)

    @property
    def current_temperature(self) -> float | None:
        return self._value_accessor.get_current_temperature(self)

    @property
    def target_temperature(self) -> float | None:
        return self._value_accessor.get_target_temperature(self)

    async def set_target_temperature(self, target_temperature: float):
        await self._value_accessor.set_target_temperature(self, target_temperature)


class ThermostatMode(IntEnum):
    Off = 1
    Comfort = 8
    Reduced = 16
    Manual = 64
    Standby = 256


class ThermostatFeature(IntEnum):
    TARGET_TEMPERATURE = 0


class ThermostatValueAccessor(DataProvider.DataSubscriberInterface):
    _data = {}

    def __init__(self, data_provider: DataProvider.DataProvider):
        self._data_provider = data_provider
        self._data_provider.subscribe(self)

    def update_status(self, status):
        if status is not None and "roomtemps" in status:
            thermostats = status["roomtemps"]
            for key in thermostats:
                if key.startswith("item"):
                    if key not in self._data:
                        self._data[key] = {}

                    if (
                        "sumstate" in thermostats[key]
                        and "value" in thermostats[key]["sumstate"]
                    ):
                        (
                            self._data[key]["actTemp"],
                            self._data[key]["setpointTemp"],
                            self._data[key]["valve"],
                            self._data[key]["mode"],
                            self._data[key]["Reserved"],
                            self._data[key]["tempAdjustment"],
                            self._data[key]["cooling"],
                            self._data[key]["sum"],
                            self._data[key]["humidity"],
                            self._data[key]["airQuality"],
                            self._data[key]["floorTemp"],
                        ) = thermostats[key]["sumstate"]["value"].split(";")

    def update_resources(self, resources):
        if resources is not None and "roomtemps" in resources:
            thermostats = resources["roomtemps"]
            for key in thermostats:
                if key.startswith("item"):
                    if key not in self._data:
                        self._data[key] = {}
                    self._data[key]["name"] = thermostats[key]["name"]

    @property
    def thermostats(self):
        result: list[Thermostat] = []
        for key in self._data:
            result.append(Thermostat(key, self._data[key]["name"], self))

        return result

    def get_features(self, thermostat: Thermostat) -> list[ThermostatFeature]:
        result = list()

        if thermostat and thermostat.id:
            if thermostat.id in self._data:
                data = self._data[thermostat.id]
                if "setpointTemp" in data and data["setpointTemp"]:
                    result.append(ThermostatFeature.TARGET_TEMPERATURE)

        return result

    def get_current_temperature(self, thermostat: Thermostat) -> float | None:
        if thermostat and thermostat.id:
            if (
                thermostat.id in self._data
                and "actTemp" in self._data[thermostat.id]
                and self._data[thermostat.id]["actTemp"]
            ):
                return float(self._data[thermostat.id]["actTemp"])
        return None

    def get_target_temperature(self, thermostat: Thermostat) -> float | None:
        if thermostat and thermostat.id:
            if (
                thermostat.id in self._data
                and "setpointTemp" in self._data[thermostat.id]
                and self._data[thermostat.id]["setpointTemp"]
            ):
                return float(self._data[thermostat.id]["setpointTemp"])
        return None

    async def set_target_temperature(
        self, thermostat: Thermostat, target_temperature: float
    ) -> None:
        if thermostat and thermostat.id:
            await self._data_provider.write_data(
                thermostat.resource_path, "S" + str(target_temperature)
            )

    def get_mode(self, thermostat: Thermostat) -> ThermostatMode | None:
        if thermostat and thermostat.id:
            if (
                thermostat.id in self._data
                and "mode" in self._data[thermostat.id]
                and self._data[thermostat.id]["mode"]
            ):
                return ThermostatMode(int(self._data[thermostat.id]["mode"]))
        return None

    async def set_mode(self, thermostat: Thermostat, mode: ThermostatMode) -> None:
        if thermostat and thermostat.id:
            await self._data_provider.write_data(
                thermostat.resource_path, "M" + str(mode.value)
            )
