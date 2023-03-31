from __future__ import annotations

from PyMyGekko import DataProvider
from PyMyGekko.resources import Entity


class EnergyMeter(Entity):
    def __init__(
        self, id: str, name: str, value_accessor: EnergyMeterValueAccessor
    ) -> None:
        super().__init__(id, name)
        self._value_accessor = value_accessor
        self._resource_path = "/energycosts/" + self.id


class EnergyMeterValueAccessor(DataProvider.DataSubscriberInterface):
    _data = {}

    def __init__(self, data_provider: DataProvider.DataProvider):
        self._data_provider = data_provider
        self._data_provider.subscribe(self)

    def update_status(self, status):
        if status is not None and "energycosts" in status:
            energyMeters = status["energycosts"]
            for key in energyMeters:
                if key.startswith("item"):
                    if key not in self._data:
                        self._data[key] = {}

                    if (
                        "sumstate" in energyMeters[key]
                        and "value" in energyMeters[key]["sumstate"]
                    ):
                        (
                            self._data[key]["actPower[kW]"],
                            self._data[key]["energyToday[kWh]"],
                            self._data[key]["energyMonth[kWh]"],
                            self._data[key]["energySum[kWh]"],
                            self._data[key]["powerMax[kW]"],
                            self._data[key]["unitEnergy[Unit]"],
                            self._data[key]["unitPower[Unit]"],
                            self._data[key]["energyToday6[kWh]"],
                            self._data[key]["energyToday12[kWh]"],
                            self._data[key]["energyToday18[kWh]"],
                            self._data[key]["energyToday24[kWh]"],
                            self._data[key]["energyYesterd6[kWh]"],
                            self._data[key]["energyYesterd12[kWh]"],
                            self._data[key]["energyYesterd18[kWh]"],
                            self._data[key]["energyYesterd24[kWh]"],
                            self._data[key]["sum"],
                            self._data[key]["energyYear[kWh]"],
                            self._data[key]["energyPeriod[kWh]"],
                            self._data[key]["energyPeriodFrom[DateTime]"],
                            self._data[key]["unknown"],
                        ) = energyMeters[key]["sumstate"]["value"].split(";")

    def update_resources(self, resources):
        if resources is not None and "energycosts" in resources:
            energyMeters = resources["energycosts"]
            for key in energyMeters:
                if key.startswith("item"):
                    if key not in self._data:
                        self._data[key] = {}
                    self._data[key]["name"] = energyMeters[key]["name"]

    @property
    def energyMeters(self):
        result: list[EnergyMeter] = []
        for key in self._data:
            result.append(EnergyMeter(key, self._data[key]["name"], self))

        return result
