from __future__ import annotations
from enum import IntEnum

from PyMyGekko import DataProvider
from PyMyGekko.resources import Entity


class Blind(Entity):
    def __init__(self, id: str, name: str, value_accessor: BlindValueAccessor) -> None:
        super().__init__(id, name)
        self._value_accessor = value_accessor
        self._resource_path = "/blinds/" + self.id

    @property
    def position(self) -> float | None:
        return self._value_accessor.get_position(self)

    async def set_position(self, position: float):
        self._value_accessor.set_position(self, position)

    @property
    def state(self) -> BlindState:
        return self._value_accessor.get_state(self)

    async def set_state(self, blind_state: BlindState):
        self._value_accessor.set_state(self, blind_state)


class BlindState(IntEnum):
    HOLD_DOWN = -2
    DOWN = -1
    STOP = 0
    UP = 1
    HOLD_UP = 2


class BlindValueAccessor(DataProvider.DataSubscriberInterface):
    _blind_data = {}

    def __init__(self, data_provider: DataProvider.DataProvider):
        self._data_provider = data_provider
        data_provider.subscribe(self)

    def update_status(self, status):
        if status != None and "blinds" in status:
            blinds = status["blinds"]
            for key in blinds:
                if key.startswith("item"):
                    if not key in self._blind_data:
                        self._blind_data[key] = {}

                    if "sumstate" in blinds[key] and "value" in blinds[key]["sumstate"]:
                        (
                            self._blind_data[key]["state"],
                            self._blind_data[key]["position"],
                            self._blind_data[key]["angle"],
                            self._blind_data[key]["sum"],
                            self._blind_data[key]["slatRotationArea"],
                        ) = blinds[key]["sumstate"]["value"].split(";")

    def update_resources(self, resources):
        if resources != None and "blinds" in resources:
            blinds = resources["blinds"]
            for key in blinds:
                if key.startswith("item"):
                    if not key in self._blind_data:
                        self._blind_data[key] = {}
                    self._blind_data[key]["name"] = blinds[key]["name"]

    @property
    def blinds(self):
        result: list[Blind] = []
        for key in self._blind_data:
            result.append(Blind(key, self._blind_data[key]["name"], self))

        return result

    def get_position(self, blind: Blind) -> float | None:
        if blind and blind.id:
            if (
                blind.id in self._blind_data
                and "position" in self._blind_data[blind.id]
            ):
                return float(self._blind_data[blind.id]["position"])
        return None

    async def set_position(self, blind: Blind, position: float) -> None:
        if blind and blind.id and position >= 0 and position <= 100.0:
            await self._data_provider.write_data(
                "/blinds/" + blind.id, "P" + str(position)
            )

    def get_state(self, blind: Blind) -> BlindState:
        if blind and blind.id:
            if blind.id in self._blind_data and "state" in self._blind_data[blind.id]:
                return BlindState(int(self._blind_data[blind.id]["state"]))
        return BlindState.STOP

    async def set_state(self, blind: Blind, blind_state: BlindState) -> None:
        if blind and blind.id:
            await self._data_provider.write_data("/blinds/" + blind.id, blind_state)
