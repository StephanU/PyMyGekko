from __future__ import annotations

from enum import IntEnum

from PyMyGekko import DataProvider
from PyMyGekko.resources import Entity


class WaterHeater(Entity):
    def __init__(
        self, id: str, name: str, value_accessor: WaterHeaterValueAccessor
    ) -> None:
        super().__init__(id, name)
        self._value_accessor = value_accessor
        self._resource_path = "/hotwater_systems/" + self.id
        self._supported_features = self._value_accessor.get_features(self)

    @property
    def supported_features(self) -> list[WaterHeaterFeature]:
        return self._supported_features

    @property
    def state(self) -> WaterHeaterState | None:
        return self._value_accessor.get_state(self)

    async def set_state(self, state: WaterHeaterState):
        await self._value_accessor.set_state(self, state)

    @property
    def target_temperature(self) -> float | None:
        return self._value_accessor.get_target_temperature(self)

    async def set_target_temperature(self, target_temperature: float):
        await self._value_accessor.set_target_temperature(self, target_temperature)


class WaterHeaterState(IntEnum):
    OFF = 0
    ON = 1


class WaterHeaterFeature(IntEnum):
    ON_OFF = 0
    TARGET_TEMPERATURE = 1


class WaterHeaterValueAccessor(DataProvider.DataSubscriberInterface):
    _data = {}

    def __init__(self, data_provider: DataProvider.DataProvider):
        self._data = {}
        self._data_provider = data_provider
        data_provider.subscribe(self)

    def update_status(self, status):
        if status is not None and "hotwater_systems" in status:
            waterHeaters = status["hotwater_systems"]
            for key in waterHeaters:
                if key.startswith("item"):
                    if key not in self._data:
                        self._data[key] = {}

                    if (
                        "sumstate" in waterHeaters[key]
                        and "value" in waterHeaters[key]["sumstate"]
                    ):
                        (
                            self._data[key]["type"],
                            self._data[key]["cooling"],
                            self._data[key]["setpointTemp"],
                            self._data[key]["topTemp"],
                            self._data[key]["bottomTemp"],
                            self._data[key]["collectorTemp"],
                            self._data[key]["state"],
                            self._data[key]["sum"],
                            *other,
                        ) = waterHeaters[key]["sumstate"]["value"].split(";")

    def update_resources(self, resources):
        if resources is not None and "hotwater_systems" in resources:
            waterHeaters = resources["hotwater_systems"]
            for key in waterHeaters:
                if key.startswith("item"):
                    if key not in self._data:
                        self._data[key] = {}
                    self._data[key]["name"] = waterHeaters[key]["name"]

    @property
    def waterHeaters(self):
        result: list[WaterHeater] = []
        for key in self._data:
            result.append(WaterHeater(key, self._data[key]["name"], self))

        return result

    def get_features(self, waterHeater: WaterHeater) -> list[WaterHeaterFeature]:
        result = list()

        if waterHeater and waterHeater.id:
            if waterHeater.id in self._data:
                data = self._data[waterHeater.id]
                if "state" in data and data["state"]:
                    result.append(WaterHeaterFeature.ON_OFF)
                if "setpointTemp" in data and data["setpointTemp"]:
                    result.append(WaterHeaterFeature.TARGET_TEMPERATURE)

        return result

    def get_state(self, waterHeater: WaterHeater) -> WaterHeaterState:
        if waterHeater and waterHeater.id:
            if (
                waterHeater.id in self._data
                and "state" in self._data[waterHeater.id]
                and self._data[waterHeater.id]["state"]
            ):
                return WaterHeaterState(int(self._data[waterHeater.id]["state"]))
        return None

    async def set_state(
        self, waterHeater: WaterHeater, state: WaterHeaterState
    ) -> None:
        if waterHeater and waterHeater.id:
            await self._data_provider.write_data(waterHeater._resource_path, state)

    def get_target_temperature(self, waterHeater: WaterHeater) -> float | None:
        if waterHeater and waterHeater.id:
            if (
                waterHeater.id in self._data
                and "setpointTemp" in self._data[waterHeater.id]
                and self._data[waterHeater.id]["setpointTemp"]
            ):
                return float(self._data[waterHeater.id]["setpointTemp"])
        return None

    async def set_target_temperature(
        self, waterHeater: WaterHeater, target_temperature: float
    ) -> None:
        if waterHeater and waterHeater.id:
            await self._data_provider.write_data(
                waterHeater._resource_path, "T" + str(target_temperature)
            )
