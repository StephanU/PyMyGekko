from __future__ import annotations

from PyMyGekko import DataProvider
from PyMyGekko.resources import Entity


class Blind(Entity):
    def __init__(self, id: str, name: str, value_accessor: BlindValueAccessor) -> None:
        super().__init__(id, name)
        self._value_accessor = value_accessor

    @property
    def position(self):
        return self._value_accessor.get_position(self)


class BlindValueAccessor(DataProvider.DataSubscriberInterface):
    _resources = None
    _status = None
    _blind_data = {}

    def __init__(self, data_provider: DataProvider.DataProvider):
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

    def get_position(self, blind: Blind) -> int | None:
        if blind and blind.id:
            if (
                blind.id in self._blind_data
                and "position" in self._blind_data[blind.id]
            ):
                return float(self._blind_data[blind.id]["position"])
        return None
