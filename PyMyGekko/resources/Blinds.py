from __future__ import annotations
from enum import IntEnum

from PyMyGekko import DataProvider
from PyMyGekko.resources import Entity


class Blind(Entity):
    def __init__(self, id: str, name: str, value_accessor: BlindValueAccessor) -> None:
        super().__init__(id, name)
        self._value_accessor = value_accessor
        self._resource_path = "/blinds/" + self.id
        self._supported_features = self._value_accessor.get_features(self)

    @property
    def supported_features(self) -> list[BlindFeature]:
        return self._supported_features

    @property
    def position(self) -> float | None:
        return self._value_accessor.get_position(self)

    async def set_position(self, position: float):
        await self._value_accessor.set_position(self, position)

    @property
    def state(self) -> BlindState | None:
        return self._value_accessor.get_state(self)

    async def set_state(self, state: BlindState):
        await self._value_accessor.set_state(self, state)

    @property
    def tilt_position(self) -> float | None:
        return self._value_accessor.get_tilt_position(self)

    async def set_tilt_position(self, position: float):
        await self._value_accessor.set_tilt_position(self, position)


class BlindState(IntEnum):
    HOLD_DOWN = -2
    DOWN = -1
    STOP = 0
    UP = 1
    HOLD_UP = 2


class BlindFeature(IntEnum):
    OPEN_CLOSE_STOP = 0
    SET_POSITION = 1
    SET_TILT_POSITION = 2


class BlindValueAccessor(DataProvider.DataSubscriberInterface):
    _data = {}

    def __init__(self, data_provider: DataProvider.DataProvider):
        self._data_provider = data_provider
        self._data_provider.subscribe(self)

    def update_status(self, status):
        if status != None and "blinds" in status:
            blinds = status["blinds"]
            for key in blinds:
                if key.startswith("item"):
                    if not key in self._data:
                        self._data[key] = {}

                    if "sumstate" in blinds[key] and "value" in blinds[key]["sumstate"]:
                        (
                            self._data[key]["state"],
                            self._data[key]["position"],
                            self._data[key]["angle"],
                            self._data[key]["sum"],
                            self._data[key]["slatRotationArea"],
                        ) = blinds[key]["sumstate"]["value"].split(";")

    def update_resources(self, resources):
        if resources != None and "blinds" in resources:
            blinds = resources["blinds"]
            for key in blinds:
                if key.startswith("item"):
                    if not key in self._data:
                        self._data[key] = {}
                    self._data[key]["name"] = blinds[key]["name"]

    @property
    def blinds(self):
        result: list[Blind] = []
        for key in self._data:
            result.append(Blind(key, self._data[key]["name"], self))

        return result

    def get_features(self, blind: Blind) -> list[BlindFeature]:
        result = list()

        if blind and blind.id:
            if blind.id in self._data:
                blind_data = self._data[blind.id]
                if "state" in blind_data and blind_data["state"]:
                    result.append(BlindFeature.OPEN_CLOSE_STOP)

                if "position" in blind_data and blind_data["position"]:
                    result.append(BlindFeature.SET_POSITION)

                if "angle" in blind_data and blind_data["angle"]:
                    result.append(BlindFeature.SET_TILT_POSITION)

        return result

    def get_position(self, blind: Blind) -> float | None:
        if blind and blind.id:
            if (
                blind.id in self._data
                and "position" in self._data[blind.id]
                and self._data[blind.id]["position"]
            ):
                return float(self._data[blind.id]["position"])
        return None

    async def set_position(self, blind: Blind, position: float) -> None:
        if blind and blind.id and position >= 0 and position <= 100.0:
            await self._data_provider.write_data(
                "/blinds/" + blind.id, "P" + str(position)
            )

    def get_tilt_position(self, blind: Blind) -> float | None:
        if blind and blind.id:
            if (
                blind.id in self._data
                and "angle" in self._data[blind.id]
                and self._data[blind.id]["angle"]
            ):
                return float(self._data[blind.id]["angle"])
        return None

    async def set_tilt_position(self, blind: Blind, position: float) -> None:
        if blind and blind.id and position >= 0 and position <= 100.0:
            await self._data_provider.write_data(
                "/blinds/" + blind.id, "S" + str(position)
            )

    def get_state(self, blind: Blind) -> BlindState | None:
        if blind and blind.id:
            if (
                blind.id in self._data
                and "state" in self._data[blind.id]
                and self._data[blind.id]["state"]
            ):
                return BlindState(int(self._data[blind.id]["state"]))
        return BlindState.NONE

    async def set_state(self, blind: Blind, state: BlindState) -> None:
        if blind and blind.id:
            await self._data_provider.write_data("/blinds/" + blind.id, state)
