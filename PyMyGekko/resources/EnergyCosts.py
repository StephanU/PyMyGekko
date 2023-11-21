from __future__ import annotations

import re

from PyMyGekko import DataProvider
from PyMyGekko.resources import Entity


class EnergyCost(Entity):
    def __init__(
        self, id: str, name: str, value_accessor: EnergyCostValueAccessor
    ) -> None:
        super().__init__(id, name)
        self._value_accessor = value_accessor
        self._resource_path = "/energycosts/" + self.id

    @property
    def sensor_data(self) -> dict[str, any]:
        return self._value_accessor.get_data(self)


class EnergyCostValueAccessor(DataProvider.DataSubscriberInterface):
    _data = {}

    def __init__(self, data_provider: DataProvider.DataProvider):
        self._data = {}
        self._data_provider = data_provider
        self._data_provider.subscribe(self)

    def _transform_value(self, description: str, value: str) -> any:
        m = re.match(r"([^\[]*)\[([^\]]*)\]", description)

        if m is None:
            return None

        typed_value = None

        unit = None if len(m.groups()) == 1 else m.group(2)

        if unit is not None and unit != "Unit" and unit != "DateTime":
            typed_value = float(value)
        else:
            typed_value = value

        return {"name": m.group(1), "unit": unit, "value": typed_value}

    def _decode_values(self, value: str) -> any:
        value_descriptions = [
            "actPower[kW]",
            "energyToday[kWh]",
            "energyMonth[kWh]",
            "energySum[kWh]",
            "powerMax[kW]",
            "unitEnergy[Unit]",
            "unitPower[Unit]",
            "energyToday6[kWh]",
            "energyToday12[kWh]",
            "energyToday18[kWh]",
            "energyToday24[kWh]",
            "energyYesterd6[kWh]",
            "energyYesterd12[kWh]",
            "energyYesterd18[kWh]",
            "energyYesterd24[kWh]",
            "sum",
            "energyYear[kWh]",
            "energyPeriod[kWh]",
            "energyPeriodFrom[DateTime]",
            "unknown",
        ]
        values = []
        for index, value_parts in enumerate(value.split(";")):
            values.append(self._transform_value(value_descriptions[index], value_parts))

        return values

    def update_status(self, status):
        if status is not None and "energycosts" in status:
            energyCosts = status["energycosts"]
            for key in energyCosts:
                if key.startswith("item"):
                    if key not in self._data:
                        self._data[key] = {}

                    if (
                        "sumstate" in energyCosts[key]
                        and "value" in energyCosts[key]["sumstate"]
                    ):
                        self._data[key]["values"] = self._decode_values(
                            energyCosts[key]["sumstate"]["value"]
                        )

    def update_resources(self, resources):
        if resources is not None and "energycosts" in resources:
            energyCosts = resources["energycosts"]
            for key in energyCosts:
                if key.startswith("item"):
                    if key not in self._data:
                        self._data[key] = {}
                    self._data[key]["name"] = energyCosts[key]["name"]

    @property
    def energyCosts(self):
        result: list[EnergyCost] = []
        for key in self._data:
            result.append(EnergyCost(key, self._data[key]["name"], self))

        return result

    def get_data(self, energy_meter: EnergyCost) -> dict[str, any]:
        if energy_meter and energy_meter.id:
            if energy_meter.id in self._data and self._data[energy_meter.id]:
                return self._data[energy_meter.id]
        return None
