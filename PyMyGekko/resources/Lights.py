from __future__ import annotations
from enum import IntEnum

from PyMyGekko import DataProvider
from PyMyGekko.resources import Entity


class Light(Entity):
    def __init__(self, id: str, name: str, value_accessor: LightValueAccessor) -> None:
        super().__init__(id, name)
        self._value_accessor = value_accessor
        self._resource_path = "/lights/" + self.id

    @property
    def state(self) -> LightState:
        return self._value_accessor.get_state(self)

    async def set_state(self, blind_state: LightState):
        await self._value_accessor.set_state(self, blind_state)


class LightState(IntEnum):
    OFF = 0
    ON = 1


class LightValueAccessor(DataProvider.DataSubscriberInterface):
    _light_data = {}

    def __init__(self, data_provider: DataProvider.DataProvider):
        self._data_provider = data_provider
        data_provider.subscribe(self)

    def update_status(self, status):
        if status != None and "lights" in status:
            lights = status["lights"]
            for key in lights:
                if key.startswith("item"):
                    if not key in self._light_data:
                        self._light_data[key] = {}

                    if "sumstate" in lights[key] and "value" in lights[key]["sumstate"]:
                        (
                            self._light_data[key]["state"],
                            self._light_data[key]["dimValue"],
                            self._light_data[key]["RGBcolor"],
                            self._light_data[key]["tunableWhite"],
                            self._light_data[key]["sum"],
                        ) = lights[key]["sumstate"]["value"].split(";")

    def update_resources(self, resources):
        if resources != None and "lights" in resources:
            lights = resources["lights"]
            for key in lights:
                if key.startswith("item"):
                    if not key in self._light_data:
                        self._light_data[key] = {}
                    self._light_data[key]["name"] = lights[key]["name"]

    @property
    def lights(self):
        result: list[Light] = []
        for key in self._light_data:
            result.append(Light(key, self._light_data[key]["name"], self))

        return result

    def get_state(self, light: Light) -> LightState:
        if light and light.id:
            if light.id in self._light_data and "state" in self._light_data[light.id]:
                return LightState(int(self._light_data[light.id]["state"]))
        return LightState.STOP

    async def set_state(self, light: Light, blind_state: LightState) -> None:
        if light and light.id:
            await self._data_provider.write_data("/lights/" + light.id, blind_state)
