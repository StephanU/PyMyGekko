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
    def state(self) -> BlindState:
        return self._value_accessor.get_state(self)

    async def set_state(self, blind_state: BlindState):
        await self._value_accessor.set_state(self, blind_state)

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
    _blinds_data = {}

    def __init__(self, data_provider: DataProvider.DataProvider):
        self._data_provider = data_provider
        self._data_provider.subscribe(self)

    def update_status(self, status):
        if status != None and "blinds" in status:
            blinds = status["blinds"]
            for key in blinds:
                if key.startswith("item"):
                    if not key in self._blinds_data:
                        self._blinds_data[key] = {}

                    if "sumstate" in blinds[key] and "value" in blinds[key]["sumstate"]:
                        (
                            self._blinds_data[key]["state"],
                            self._blinds_data[key]["position"],
                            self._blinds_data[key]["angle"],
                            self._blinds_data[key]["sum"],
                            self._blinds_data[key]["slatRotationArea"],
                        ) = blinds[key]["sumstate"]["value"].split(";")

    def update_resources(self, resources):
        if resources != None and "blinds" in resources:
            blinds = resources["blinds"]
            for key in blinds:
                if key.startswith("item"):
                    if not key in self._blinds_data:
                        self._blinds_data[key] = {}
                    self._blinds_data[key]["name"] = blinds[key]["name"]

    @property
    def blinds(self):
        result: list[Blind] = []
        for key in self._blinds_data:
            result.append(Blind(key, self._blinds_data[key]["name"], self))

        return result

    def get_features(self, blind: Blind) -> list[BlindFeature]:
        result = list()

        if blind and blind.id:
            if blind.id in self._blinds_data:
                blind_data = self._blinds_data[blind.id]
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
                blind.id in self._blinds_data
                and "position" in self._blinds_data[blind.id]
                and self._blinds_data[blind.id]["position"]
            ):
                return float(self._blinds_data[blind.id]["position"])
        return None

    async def set_position(self, blind: Blind, position: float) -> None:
        if blind and blind.id and position >= 0 and position <= 100.0:
            await self._data_provider.write_data(
                "/blinds/" + blind.id, "P" + str(position)
            )

    def get_tilt_position(self, blind: Blind) -> float | None:
        if blind and blind.id:
            if (
                blind.id in self._blinds_data
                and "angle" in self._blinds_data[blind.id]
                and self._blinds_data[blind.id]["angle"]
            ):
                return float(self._blinds_data[blind.id]["angle"])
        return None

    async def set_tilt_position(self, blind: Blind, position: float) -> None:
        if blind and blind.id and position >= 0 and position <= 100.0:
            await self._data_provider.write_data(
                "/blinds/" + blind.id, "S" + str(position)
            )

    def get_state(self, blind: Blind) -> BlindState:
        if blind and blind.id:
            if (
                blind.id in self._blinds_data
                and "state" in self._blinds_data[blind.id]
                and self._blinds_data[blind.id]["state"]
            ):
                return BlindState(int(self._blinds_data[blind.id]["state"]))
        return BlindState.STOP

    async def set_state(self, blind: Blind, blind_state: BlindState) -> None:
        if blind and blind.id:
            await self._data_provider.write_data("/blinds/" + blind.id, blind_state)
