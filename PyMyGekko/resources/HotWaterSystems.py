from __future__ import annotations

from enum import IntEnum

from PyMyGekko import DataProvider
from PyMyGekko.resources import Entity


class HotWaterSystem(Entity):
    def __init__(
        self, id: str, name: str, value_accessor: HotWaterSystemValueAccessor
    ) -> None:
        super().__init__(id, name)
        self._value_accessor = value_accessor
        self._resource_path = "/hotwater_systems/" + self.id
        self._supported_features = self._value_accessor.get_features(self)

    @property
    def supported_features(self) -> list[HotWaterSystemFeature]:
        return self._supported_features

    @property
    def state(self) -> HotWaterSystemState | None:
        return self._value_accessor.get_state(self)

    async def set_state(self, state: HotWaterSystemState):
        await self._value_accessor.set_state(self, state)

    @property
    def target_temperature(self) -> float | None:
        return self._value_accessor.get_target_temperature(self)

    async def set_target_temperature(self, target_temperature: float):
        await self._value_accessor.set_target_temperature(self, target_temperature)

    @property
    def current_temperature_top(self) -> float | None:
        return self._value_accessor.get_current_temperature_top(self)

    @property
    def current_temperature_bottom(self) -> float | None:
        return self._value_accessor.get_current_temperature_bottom(self)


class HotWaterSystemState(IntEnum):
    OFF = 0
    ON = 1


class HotWaterSystemFeature(IntEnum):
    ON_OFF = 0
    TARGET_TEMPERATURE = 1


class HotWaterSystemValueAccessor(DataProvider.DataSubscriberInterface):
    _data = {}

    def __init__(self, data_provider: DataProvider.DataProvider):
        self._data = {}
        self._data_provider = data_provider
        data_provider.subscribe(self)

    def update_status(self, status):
        if status is not None and "hotwater_systems" in status:
            hotWaterSystems = status["hotwater_systems"]
            for key in hotWaterSystems:
                if key.startswith("item"):
                    if key not in self._data:
                        self._data[key] = {}

                    if (
                        "sumstate" in hotWaterSystems[key]
                        and "value" in hotWaterSystems[key]["sumstate"]
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
                        ) = hotWaterSystems[key]["sumstate"]["value"].split(";")

    def update_resources(self, resources):
        if resources is not None and "hotwater_systems" in resources:
            hotWaterSystems = resources["hotwater_systems"]
            for key in hotWaterSystems:
                if key.startswith("item"):
                    if key not in self._data:
                        self._data[key] = {}
                    self._data[key]["name"] = hotWaterSystems[key]["name"]

    @property
    def hotWaterSystems(self):
        result: list[HotWaterSystem] = []
        for key in self._data:
            result.append(HotWaterSystem(key, self._data[key]["name"], self))

        return result

    def get_features(
        self, hotWaterSystem: HotWaterSystem
    ) -> list[HotWaterSystemFeature]:
        result = list()

        if hotWaterSystem and hotWaterSystem.id:
            if hotWaterSystem.id in self._data:
                data = self._data[hotWaterSystem.id]
                if "state" in data and data["state"]:
                    result.append(HotWaterSystemFeature.ON_OFF)
                if "setpointTemp" in data and data["setpointTemp"]:
                    result.append(HotWaterSystemFeature.TARGET_TEMPERATURE)

        return result

    def get_state(self, hotWaterSystem: HotWaterSystem) -> HotWaterSystemState:
        if hotWaterSystem and hotWaterSystem.id:
            if (
                hotWaterSystem.id in self._data
                and "state" in self._data[hotWaterSystem.id]
                and self._data[hotWaterSystem.id]["state"]
            ):
                return HotWaterSystemState(int(self._data[hotWaterSystem.id]["state"]))
        return None

    async def set_state(
        self, hotWaterSystem: HotWaterSystem, state: HotWaterSystemState
    ) -> None:
        if hotWaterSystem and hotWaterSystem.id:
            await self._data_provider.write_data(hotWaterSystem._resource_path, state)

    def get_target_temperature(self, hotWaterSystem: HotWaterSystem) -> float | None:
        if hotWaterSystem and hotWaterSystem.id:
            if (
                hotWaterSystem.id in self._data
                and "setpointTemp" in self._data[hotWaterSystem.id]
                and self._data[hotWaterSystem.id]["setpointTemp"]
            ):
                return float(self._data[hotWaterSystem.id]["setpointTemp"])
        return None

    async def set_target_temperature(
        self, hotWaterSystem: HotWaterSystem, target_temperature: float
    ) -> None:
        if hotWaterSystem and hotWaterSystem.id:
            await self._data_provider.write_data(
                hotWaterSystem._resource_path, "T" + str(target_temperature)
            )

    def get_current_temperature_top(
        self, hotWaterSystem: HotWaterSystem
    ) -> float | None:
        if hotWaterSystem and hotWaterSystem.id:
            if (
                hotWaterSystem.id in self._data
                and "topTemp" in self._data[hotWaterSystem.id]
                and self._data[hotWaterSystem.id]["topTemp"]
            ):
                return float(self._data[hotWaterSystem.id]["topTemp"])
        return None

    def get_current_temperature_bottom(
        self, hotWaterSystem: HotWaterSystem
    ) -> float | None:
        if hotWaterSystem and hotWaterSystem.id:
            if (
                hotWaterSystem.id in self._data
                and "bottomTemp" in self._data[hotWaterSystem.id]
                and self._data[hotWaterSystem.id]["bottomTemp"]
            ):
                return float(self._data[hotWaterSystem.id]["bottomTemp"])
        return None
