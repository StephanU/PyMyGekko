from __future__ import annotations

from enum import IntEnum

from PyMyGekko import DataProvider
from PyMyGekko.resources import Entity


class Load(Entity):
    def __init__(self, id: str, name: str, value_accessor: LoadValueAccessor) -> None:
        super().__init__(id, name)
        self._value_accessor = value_accessor
        self._resource_path = "/loads/" + self.id
        self._supported_features = self._value_accessor.get_features(self)

    @property
    def supported_features(self) -> list[LoadFeature]:
        return self._supported_features

    @property
    def state(self) -> LoadState | None:
        return self._value_accessor.get_state(self)

    async def set_state(self, state: LoadState):
        await self._value_accessor.set_state(self, state)


class LoadState(IntEnum):
    OFF = 0
    ON_IMPULSE = 1
    ON_PERMANENT = 2


class LoadFeature(IntEnum):
    ON_OFF = 0


class LoadValueAccessor(DataProvider.DataSubscriberInterface):
    _data = {}

    def __init__(self, data_provider: DataProvider.DataProvider):
        self._data = {}
        self._data_provider = data_provider
        data_provider.subscribe(self)

    def update_status(self, status):
        if status is not None and "loads" in status:
            loads = status["loads"]
            for key in loads:
                if key.startswith("item"):
                    if key not in self._data:
                        self._data[key] = {}

                    if "sumstate" in loads[key] and "value" in loads[key]["sumstate"]:
                        (
                            self._data[key]["currentState"],
                            self._data[key]["elementInfo"],
                            *other,
                        ) = loads[key]["sumstate"]["value"].split(";")

    def update_resources(self, resources):
        if resources is not None and "loads" in resources:
            loads = resources["loads"]
            for key in loads:
                if key.startswith("item"):
                    if key not in self._data:
                        self._data[key] = {}
                    self._data[key]["name"] = loads[key]["name"]

    @property
    def loads(self):
        result: list[Load] = []
        for key in self._data:
            result.append(Load(key, self._data[key]["name"], self))

        return result

    def get_features(self, load: Load) -> list[LoadFeature]:
        result = list()

        if load and load.id:
            if load.id in self._data:
                data = self._data[load.id]
                if "currentState" in data and data["currentState"]:
                    result.append(LoadFeature.ON_OFF)
        return result

    def get_state(self, load: Load) -> LoadState:
        if load and load.id:
            if (
                load.id in self._data
                and "currentState" in self._data[load.id]
                and self._data[load.id]["currentState"]
            ):
                return LoadState(int(self._data[load.id]["currentState"]))
        return None

    async def set_state(self, load: Load, state: LoadState) -> None:
        if load and load.id:
            await self._data_provider.write_data(load._resource_path, state)
