from __future__ import annotations

from enum import IntEnum

from PyMyGekko import DataProvider
from PyMyGekko.resources import Entity


class Switch(Entity):
    def __init__(self, id: str, name: str, value_accessor: SwitchValueAccessor) -> None:
        super().__init__(id, name)
        self._value_accessor = value_accessor
        self._resource_path = "/loads/" + self.id
        self._supported_features = self._value_accessor.get_features(self)

    @property
    def supported_features(self) -> list[SwitchFeature]:
        return self._supported_features

    @property
    def state(self) -> SwitchState | None:
        return self._value_accessor.get_state(self)

    async def set_state(self, state: SwitchState):
        await self._value_accessor.set_state(self, state)


class SwitchState(IntEnum):
    OFF = 0
    ON_IMPULSE = 1
    ON_PERMANENT = 2


class SwitchFeature(IntEnum):
    ON_OFF = 0


class SwitchValueAccessor(DataProvider.DataSubscriberInterface):
    _data = {}

    def __init__(self, data_provider: DataProvider.DataProvider):
        self._data = {}
        self._data_provider = data_provider
        data_provider.subscribe(self)

    def update_status(self, status):
        if status is not None and "loads" in status:
            switches = status["loads"]
            for key in switches:
                if key.startswith("item"):
                    if key not in self._data:
                        self._data[key] = {}

                    if (
                        "sumstate" in switches[key]
                        and "value" in switches[key]["sumstate"]
                    ):
                        (
                            self._data[key]["state"],
                            self._data[key]["elementInfo"],
                            *other,
                        ) = switches[key]["sumstate"]["value"].split(";")

    def update_resources(self, resources):
        if resources is not None and "loads" in resources:
            switches = resources["loads"]
            for key in switches:
                if key.startswith("item"):
                    if key not in self._data:
                        self._data[key] = {}
                    self._data[key]["name"] = switches[key]["name"]

    @property
    def switches(self):
        result: list[Switch] = []
        for key in self._data:
            result.append(Switch(key, self._data[key]["name"], self))

        return result

    def get_features(self, switch: Switch) -> list[SwitchFeature]:
        result = list()

        if switch and switch.id:
            if switch.id in self._data:
                data = self._data[switch.id]
                if "state" in data and data["state"]:
                    result.append(SwitchFeature.ON_OFF)
        return result

    def get_state(self, switch: Switch) -> SwitchState:
        if switch and switch.id:
            if (
                switch.id in self._data
                and "state" in self._data[switch.id]
                and self._data[switch.id]["state"]
            ):
                return SwitchState(int(self._data[switch.id]["state"]))
        return None

    async def set_state(self, switch: Switch, state: SwitchState) -> None:
        if switch and switch.id:
            await self._data_provider.write_data(switch._resource_path, state)
