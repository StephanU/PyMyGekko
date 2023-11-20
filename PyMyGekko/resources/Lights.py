from __future__ import annotations

from enum import IntEnum
from math import ceil

from PyMyGekko import DataProvider
from PyMyGekko.resources import Entity


class Light(Entity):
    def __init__(self, id: str, name: str, value_accessor: LightValueAccessor) -> None:
        super().__init__(id, name)
        self._value_accessor = value_accessor
        self._resource_path = "/lights/" + self.id
        self._supported_features = self._value_accessor.get_features(self)

    @property
    def supported_features(self) -> list[LightFeature]:
        return self._supported_features

    @property
    def state(self) -> LightState | None:
        return self._value_accessor.get_state(self)

    async def set_state(self, state: LightState):
        await self._value_accessor.set_state(self, state)

    @property
    def brightness(self) -> int | None:
        return self._value_accessor.get_brightness(self)

    async def set_brightness(self, brightness: int):
        await self._value_accessor.set_brightness(self, brightness)

    @property
    def rgb_color(self) -> tuple[int, int, int] | None:
        return self._value_accessor.get_rgb_color(self)

    async def set_rgb_color(self, rgb_color: tuple[int, int, int]):
        await self._value_accessor.set_rgb_color(self, rgb_color)


class LightState(IntEnum):
    OFF = 0
    ON = 1


class LightFeature(IntEnum):
    ON_OFF = 0
    DIMMABLE = 1
    RGB_COLOR = 2


class LightValueAccessor(DataProvider.DataSubscriberInterface):
    _data = {}

    def __init__(self, data_provider: DataProvider.DataProvider):
        self._data = {}
        self._data_provider = data_provider
        data_provider.subscribe(self)

    def update_status(self, status):
        if status is not None and "lights" in status:
            lights = status["lights"]
            for key in lights:
                if key.startswith("item"):
                    if key not in self._data:
                        self._data[key] = {}

                    if "sumstate" in lights[key] and "value" in lights[key]["sumstate"]:
                        (
                            self._data[key]["currentState"],
                            self._data[key]["dimLevel"],
                            self._data[key]["rgbColor"],
                            self._data[key]["tunableWhiteLevel"],
                            self._data[key]["elementInfo"],
                            *other,
                        ) = lights[key]["sumstate"]["value"].split(";")

    def update_resources(self, resources):
        if resources is not None and "lights" in resources:
            lights = resources["lights"]
            for key in lights:
                if key.startswith("item"):
                    if key not in self._data:
                        self._data[key] = {}
                    self._data[key]["name"] = lights[key]["name"]

    @property
    def lights(self):
        result: list[Light] = []
        for key in self._data:
            result.append(Light(key, self._data[key]["name"], self))

        return result

    def get_features(self, light: Light) -> list[LightFeature]:
        result = list()

        if light and light.id:
            if light.id in self._data:
                data = self._data[light.id]
                if "currentState" in data and data["currentState"]:
                    result.append(LightFeature.ON_OFF)
                if "dimLevel" in data and data["dimLevel"]:
                    result.append(LightFeature.DIMMABLE)
                if "rgbColor" in data and data["rgbColor"]:
                    result.append(LightFeature.RGB_COLOR)

        return result

    def get_state(self, light: Light) -> LightState:
        if light and light.id:
            if (
                light.id in self._data
                and "currentState" in self._data[light.id]
                and self._data[light.id]["currentState"]
            ):
                return LightState(int(self._data[light.id]["currentState"]))
        return None

    async def set_state(self, light: Light, state: LightState) -> None:
        if light and light.id:
            await self._data_provider.write_data(light._resource_path, state)

    def get_brightness(self, light: Light) -> int | None:
        if light and light.id:
            if (
                light.id in self._data
                and "dimLevel" in self._data[light.id]
                and self._data[light.id]["dimLevel"]
            ):
                return ceil(float(self._data[light.id]["dimLevel"]))
        return None

    async def set_brightness(self, light: Light, brightness: int) -> None:
        if light and light.id and brightness >= 0 and brightness <= 100:
            await self._data_provider.write_data(
                light._resource_path, "D" + str(brightness)
            )

    def get_rgb_color(self, light: Light) -> tuple[int, int, int] | None:
        if light and light.id:
            if (
                light.id in self._data
                and "rgbColor" in self._data[light.id]
                and self._data[light.id]["rgbColor"]
            ):
                decimal_rgb_color = int(self._data[light.id]["rgbColor"])
                return ColorUtilities.decimal_to_rgb(decimal_rgb_color)
        return None

    async def set_rgb_color(
        self, light: Light, rgb_color: tuple[int, int, int]
    ) -> None:
        if (
            light
            and light.id
            and rgb_color[0] >= 0
            and rgb_color[0] <= 255
            and rgb_color[1] >= 0
            and rgb_color[1] <= 255
            and rgb_color[2] >= 0
            and rgb_color[2] <= 255
        ):
            decimal_rbg_color = (
                (rgb_color[0] << 16) + (rgb_color[1] << 8) + rgb_color[2]
            )
            await self._data_provider.write_data(
                light._resource_path, "C" + str(decimal_rbg_color)
            )


class ColorUtilities:
    @staticmethod
    def decimal_to_rgb(decimal_rgb_color: int) -> tuple[int, int, int]:
        return (
            (decimal_rgb_color >> 16) & 255,
            (decimal_rgb_color >> 8) & 255,
            decimal_rgb_color & 255,
        )
