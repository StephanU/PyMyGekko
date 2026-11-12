"""MyGekko AlarmSystems implementation

The myGEKKO system "alarmsystem" mirrors an external intrusion alarm panel
(currently TELENOT complex 400 / hiplex 8400). myGEKKO creates one item per
security area ("Sicherungsbereich") of the panel. Every item carries the state
of its own area plus some values of the whole panel (device model, panel state
and the input group states), which are identical in all items.
"""
from __future__ import annotations

from enum import IntEnum

from PyMyGekko.data_provider import DataProviderBase
from PyMyGekko.data_provider import EntityValueAccessor
from PyMyGekko.resources import Entity


class AlarmSystem(Entity):
    """Class for a MyGekko AlarmSystem item (one security area of the panel)"""

    def __init__(
        self, entity_id: str, name: str, value_accessor: AlarmSystemValueAccessor
    ) -> None:
        super().__init__(entity_id, name, "/alarmsystem/")
        self._value_accessor = value_accessor
        self._supported_features = self._value_accessor.get_features(self)

    @property
    def supported_features(self) -> list[AlarmSystemFeature]:
        """Returns the supported features"""
        return self._supported_features

    @property
    def alarm_state(self) -> AlarmSystemAlarmState | None:
        """Returns the alarm state of this security area"""
        return _to_enum(
            AlarmSystemAlarmState, self._value_accessor.get_value(self, "alarmState")
        )

    @property
    def sharp_state(self) -> AlarmSystemSharpState | None:
        """Returns the arming state of this security area"""
        return _to_enum(
            AlarmSystemSharpState, self._value_accessor.get_value(self, "sharpState")
        )

    @property
    def device_model(self) -> AlarmSystemDeviceModel | None:
        """Returns the model of the alarm panel"""
        return _to_enum(
            AlarmSystemDeviceModel,
            self._value_accessor.get_value(self, "deviceModel"),
        )

    @property
    def device_state(self) -> AlarmSystemDeviceState | None:
        """Returns the state of the alarm panel"""
        return _to_enum(
            AlarmSystemDeviceState,
            self._value_accessor.get_value(self, "alarmDeviceState"),
        )

    @property
    def active_input_groups(self) -> list[int] | None:
        """Returns the indexes of the active input groups ("Meldebereiche").

        The panel reports one bit per input group (up to 512), as a hex string.
        Index 0 is the lowest bit of the last hex character. An input group is
        active while it is triggered, e.g. an open window or a motion detector.
        """
        value = self._value_accessor.get_value(self, "inputGroupsState")
        if value is None:
            return None

        try:
            bits = int(value, 16)
        except ValueError:
            return None

        return [index for index in range(len(value) * 4) if bits >> index & 1]

    @property
    def input_group_count(self) -> int | None:
        """Returns the number of input groups the panel reports"""
        value = self._value_accessor.get_value(self, "inputGroupsState")
        return len(value) * 4 if value is not None else None

    async def set_sharp_state(self, state: AlarmSystemSharpState):
        """Arms or disarms this security area"""
        await self._value_accessor.set_sharp_state(self, state)


class AlarmSystemAlarmState(IntEnum):
    """MyGekko AlarmSystem alarm state of a security area"""

    OK = 0
    ALARM = 1


class AlarmSystemSharpState(IntEnum):
    """MyGekko AlarmSystem arming state of a security area"""

    NO_INFO = 0
    UNSHARP = 1
    INTERNAL_SHARP = 2
    EXTERNAL_SHARP = 3


class AlarmSystemDeviceModel(IntEnum):
    """MyGekko AlarmSystem alarm panel model"""

    COMPLEX400_V2 = 3
    HIPLEX8400_V2 = 4


class AlarmSystemDeviceState(IntEnum):
    """MyGekko AlarmSystem alarm panel state"""

    OK = 0
    ALARM = 1
    FAULT = 2


class AlarmSystemFeature(IntEnum):
    """MyGekko AlarmSystem feature, derived from the commands the item accepts"""

    DISARM = 0
    ARM_INTERNAL = 1
    ARM_EXTERNAL = 2


_FEATURE_BY_COMMAND = {
    AlarmSystemSharpState.UNSHARP: AlarmSystemFeature.DISARM,
    AlarmSystemSharpState.INTERNAL_SHARP: AlarmSystemFeature.ARM_INTERNAL,
    AlarmSystemSharpState.EXTERNAL_SHARP: AlarmSystemFeature.ARM_EXTERNAL,
}


def _to_enum(enum_type, value: str | None):
    """Convert a raw value, None if it is missing or unknown to the enum"""
    if value is None:
        return None
    try:
        return enum_type(int(value))
    except ValueError:
        return None


def _parse_commands(scmd_format: str) -> list[int]:
    """Parse the accepted values of a scmd format like "2|3 (Internal|External)"."""
    values = scmd_format.split("(", 1)[0]
    result = []
    for value in values.split("|"):
        try:
            result.append(int(value.strip()))
        except ValueError:
            continue
    return result


class AlarmSystemValueAccessor(EntityValueAccessor):
    """AlarmSystems value accessor"""

    SUM_STATE_FIELDS = [
        "alarmState",
        "deviceModel",
        "sharpState",
        "inputGroupsState",
        "alarmDeviceState",
    ]

    def __init__(self, data_provider: DataProviderBase):
        super().__init__()
        self._data_provider = data_provider
        data_provider.subscribe(self)

    def update_status(self, status, hardware):
        if status is not None and "alarmsystem" in status:
            alarm_systems = status["alarmsystem"]
            for key in alarm_systems:
                if key.startswith("item"):
                    if key not in self._data:
                        self._data[key] = {}

                    if (
                        "sumstate" in alarm_systems[key]
                        and "value" in alarm_systems[key]["sumstate"]
                    ):
                        values = alarm_systems[key]["sumstate"]["value"].split(";")
                        for name, value in zip(self.SUM_STATE_FIELDS, values):
                            self._data[key][name] = value

    def update_resources(self, resources):
        if resources is not None and "alarmsystem" in resources:
            alarm_systems = resources["alarmsystem"]
            for key in alarm_systems:
                if key.startswith("item"):
                    if key not in self._data:
                        self._data[key] = {}
                    self._data[key]["name"] = alarm_systems[key]["name"]

                    scmd = alarm_systems[key].get("scmd")
                    if isinstance(scmd, dict) and "value" in scmd:
                        self._data[key]["commands"] = _parse_commands(scmd["value"])

    @property
    def alarm_systems(self):
        """Returns the alarm system items read from MyGekko"""
        result: list[AlarmSystem] = []
        for key, data in self._data.items():
            if "name" in data:
                result.append(AlarmSystem(key, data["name"], self))

        return result

    def get_features(self, alarm_system: AlarmSystem) -> list[AlarmSystemFeature]:
        """Returns the supported features"""
        result = []

        if alarm_system and alarm_system.entity_id in self._data:
            commands = self._data[alarm_system.entity_id].get("commands", [])
            for state, feature in _FEATURE_BY_COMMAND.items():
                if int(state) in commands:
                    result.append(feature)

        return result

    async def set_sharp_state(
        self, alarm_system: AlarmSystem, state: AlarmSystemSharpState
    ) -> None:
        """Sets the arming state"""
        if alarm_system and alarm_system.entity_id:
            feature = _FEATURE_BY_COMMAND.get(state)
            if feature is None or feature not in self.get_features(alarm_system):
                raise ValueError(
                    f"{alarm_system.resource_path} does not accept the command {state!r}"
                )
            await self._data_provider.write_data(
                alarm_system.resource_path, str(int(state))
            )
