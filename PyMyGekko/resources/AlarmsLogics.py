from __future__ import annotations

from PyMyGekko import DataProvider
from PyMyGekko.resources import Entity


class AlarmsLogic(Entity):
    def __init__(
        self, id: str, name: str, value_accessor: AlarmsLogicValueAccessor
    ) -> None:
        super().__init__(id, name)
        self._value_accessor = value_accessor
        self._resource_path = "/alarms_logics/" + self.id

    @property
    def value(self) -> float | None:
        return self._value_accessor.get_value(self)


class AlarmsLogicValueAccessor(DataProvider.DataSubscriberInterface):
    _data = {}

    def __init__(self, data_provider: DataProvider.DataProvider):
        self._data = {}
        self._data_provider = data_provider
        data_provider.subscribe(self)

    def update_status(self, status):
        if status is not None and "alarms_logics" in status:
            alarmsLogics = status["alarms_logics"]
            for key in alarmsLogics:
                if key.startswith("item"):
                    if key not in self._data:
                        self._data[key] = {}

                    if (
                        "sumstate" in alarmsLogics[key]
                        and "value" in alarmsLogics[key]["sumstate"]
                    ):
                        (
                            self._data[key]["currentValue"],
                            *other,
                        ) = alarmsLogics[key][
                            "sumstate"
                        ]["value"].split(";")

    def update_resources(self, resources):
        if resources is not None and "alarms_logics" in resources:
            alarmsLogics = resources["alarms_logics"]
            for key in alarmsLogics:
                if key.startswith("item"):
                    if key not in self._data:
                        self._data[key] = {}
                    self._data[key]["name"] = alarmsLogics[key]["name"]

    @property
    def alarmsLogics(self):
        result: list[AlarmsLogic] = []
        for key in self._data:
            result.append(AlarmsLogic(key, self._data[key]["name"], self))

        return result

    def get_value(self, alarmsLogic: AlarmsLogic) -> float | None:
        if alarmsLogic and alarmsLogic.id:
            if (
                alarmsLogic.id in self._data
                and "currentValue" in self._data[alarmsLogic.id]
                and self._data[alarmsLogic.id]["currentValue"]
            ):
                return float(self._data[alarmsLogic.id]["currentValue"])
        return None
