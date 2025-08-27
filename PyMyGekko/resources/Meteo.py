"""MyGekko Meteos implementation"""
from __future__ import annotations

import logging

from PyMyGekko.data_provider import DataProviderBase
from PyMyGekko.data_provider import EntityValueAccessor
from PyMyGekko.resources import ReadOnlyEntity


_LOGGER: logging.Logger = logging.getLogger(__name__)


class Meteo(ReadOnlyEntity):
    """Class for MyGekko Meteo"""

    def __init__(
        self, entity_id: str, name: str, value_accessor: MeteoValueAccessor
    ) -> None:
        super().__init__(entity_id, name)
        self._value_accessor = value_accessor

    @property
    def sensor_data(self) -> dict[str, any]:
        """Returns the sensor data"""
        return self._value_accessor.get_data(self)


class MeteoValueAccessor(EntityValueAccessor):
    """Meteo value accessor"""

    def __init__(self, data_provider: DataProviderBase):
        self._data = {}
        self._data_provider = data_provider
        self._data_provider.subscribe(self)

    def update_status(self, status, hardware):
        if status is not None and "globals" in status:
            globals = status["globals"]
            if globals is not None and "meteo" in globals:
                meteo = globals["meteo"]

                for key in meteo:
                    if key not in self._data:
                        self._data[key] = {}

                    if "value" in meteo[key]:
                        self._data[key] = meteo[key]["value"]

    def update_resources(self, resources):
        """Nothing to do here since Meteo data is in status and no additional resources are available"""

    @property
    def meteo(self):
        """Returns the meteo read from MyGekko"""
        return Meteo("meteo", "meteo", self)

    def get_data(self, meteo: Meteo) -> dict[str, any]:
        """Returns the data of the given meteo"""
        return self._data
