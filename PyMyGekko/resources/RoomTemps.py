from __future__ import annotations

from enum import IntEnum

from PyMyGekko import DataProvider
from PyMyGekko.resources import Entity


class RoomTemp(Entity):
    def __init__(
        self, id: str, name: str, value_accessor: RoomTempsValueAccessor
    ) -> None:
        super().__init__(id, name)
        self._value_accessor = value_accessor
        self._resource_path = "/roomtemps/" + self.id
        self._supported_features = self._value_accessor.get_features(self)

    @property
    def resource_path(self) -> str:
        return self._resource_path

    @property
    def supported_features(self) -> list[RoomTempsFeature]:
        return self._supported_features

    @property
    def working_mode(self) -> RoomTempsMode | None:
        return self._value_accessor.get_working_mode(self)

    async def set_working_mode(self, workingMode: RoomTempsMode):
        await self._value_accessor.set_working_mode(self, workingMode)

    @property
    def current_temperature(self) -> float | None:
        return self._value_accessor.get_current_temperature(self)

    @property
    def target_temperature(self) -> float | None:
        return self._value_accessor.get_target_temperature(self)

    async def set_target_temperature(self, target_temperature: float):
        await self._value_accessor.set_target_temperature(self, target_temperature)


class RoomTempsMode(IntEnum):
    Off = 1
    Comfort = 8
    Reduced = 16
    Manual = 64
    Standby = 256


class RoomTempsFeature(IntEnum):
    TARGET_TEMPERATURE = 0


class RoomTempsValueAccessor(DataProvider.DataSubscriberInterface):
    _data = {}

    def __init__(self, data_provider: DataProvider.DataProvider):
        self._data = {}
        self._data_provider = data_provider
        self._data_provider.subscribe(self)

    def update_status(self, status):
        if status is not None and "roomtemps" in status:
            roomTemps = status["roomtemps"]
            for key in roomTemps:
                if key.startswith("item"):
                    if key not in self._data:
                        self._data[key] = {}

                    if (
                        "sumstate" in roomTemps[key]
                        and "value" in roomTemps[key]["sumstate"]
                    ):
                        (
                            self._data[key]["temperatureValue"],
                            self._data[key]["temperatureSetPointValue"],
                            self._data[key]["valveOpeningLevel"],
                            self._data[key]["workingMode"],
                            self._data[key]["Reserved"],
                            self._data[key]["temperatureAdjustmentValue"],
                            self._data[key]["coolingModeState"],
                            self._data[key]["elementInfo"],
                            self._data[key]["relativeHumidityLevel"],
                            self._data[key]["airQualityLevel"],
                            self._data[key]["floorTemperatureValue"],
                            *other,
                        ) = roomTemps[key]["sumstate"]["value"].split(";")

    def update_resources(self, resources):
        if resources is not None and "roomtemps" in resources:
            roomTemps = resources["roomtemps"]
            for key in roomTemps:
                if key.startswith("item"):
                    if key not in self._data:
                        self._data[key] = {}
                    self._data[key]["name"] = roomTemps[key]["name"]

    @property
    def roomTemps(self):
        result: list[RoomTemp] = []
        for key in self._data:
            result.append(RoomTemp(key, self._data[key]["name"], self))

        return result

    def get_features(self, roomTemp: RoomTemp) -> list[RoomTempsFeature]:
        result = list()

        if roomTemp and roomTemp.id:
            if roomTemp.id in self._data:
                data = self._data[roomTemp.id]
                if (
                    "temperatureSetPointValue" in data
                    and data["temperatureSetPointValue"]
                ):
                    result.append(RoomTempsFeature.TARGET_TEMPERATURE)

        return result

    def get_current_temperature(self, roomTemp: RoomTemp) -> float | None:
        if roomTemp and roomTemp.id:
            if (
                roomTemp.id in self._data
                and "temperatureValue" in self._data[roomTemp.id]
                and self._data[roomTemp.id]["temperatureValue"]
            ):
                return float(self._data[roomTemp.id]["temperatureValue"])
        return None

    def get_target_temperature(self, roomTemp: RoomTemp) -> float | None:
        if roomTemp and roomTemp.id:
            if (
                roomTemp.id in self._data
                and "temperatureSetPointValue" in self._data[roomTemp.id]
                and self._data[roomTemp.id]["temperatureSetPointValue"]
            ):
                return float(self._data[roomTemp.id]["temperatureSetPointValue"])
        return None

    async def set_target_temperature(
        self, roomTemp: RoomTemp, target_temperature: float
    ) -> None:
        if roomTemp and roomTemp.id:
            await self._data_provider.write_data(
                roomTemp.resource_path, "S" + str(target_temperature)
            )

    def get_working_mode(self, roomTemp: RoomTemp) -> RoomTempsMode | None:
        if roomTemp and roomTemp.id:
            if (
                roomTemp.id in self._data
                and "workingMode" in self._data[roomTemp.id]
                and self._data[roomTemp.id]["workingMode"]
            ):
                return RoomTempsMode(int(self._data[roomTemp.id]["workingMode"]))
        return None

    async def set_working_mode(
        self, roomTemp: RoomTemp, workingMode: RoomTempsMode
    ) -> None:
        if roomTemp and roomTemp.id:
            await self._data_provider.write_data(
                roomTemp.resource_path, "M" + str(workingMode.value)
            )
