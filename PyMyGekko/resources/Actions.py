from __future__ import annotations

from enum import IntEnum

from PyMyGekko import DataProvider
from PyMyGekko.resources import Entity


class Action(Entity):
    def __init__(self, id: str, name: str, value_accessor: ActionValueAccessor) -> None:
        super().__init__(id, name)
        self._value_accessor = value_accessor
        self._resource_path = "/actions/" + self.id
        self._supported_features = self._value_accessor.get_features(self)

    @property
    def supported_features(self) -> list[ActionFeature]:
        return self._supported_features

    @property
    def state(self) -> ActionState | None:
        return self._value_accessor.get_state(self)

    async def set_state(self, state: ActionState):
        await self._value_accessor.set_state(self, state)


class ActionState(IntEnum):
    OFF = 0
    ON = 1


class ActionFeature(IntEnum):
    ON_OFF = 0


class ActionValueAccessor(DataProvider.DataSubscriberInterface):
    _data = {}

    def __init__(self, data_provider: DataProvider.DataProvider):
        self._data = {}
        self._data_provider = data_provider
        data_provider.subscribe(self)

    def update_status(self, status):
        if status is not None and "actions" in status:
            actions = status["actions"]
            for key in actions:
                if key.startswith("item"):
                    if key not in self._data:
                        self._data[key] = {}

                    if (
                        "sumstate" in actions[key]
                        and "value" in actions[key]["sumstate"]
                    ):
                        (
                            self._data[key]["currentState"],
                            self._data[key]["startConditionState"],
                            self._data[key]["elementInfo"],
                            *other,
                        ) = actions[key]["sumstate"]["value"].split(";")

    def update_resources(self, resources):
        if resources is not None and "actions" in resources:
            actions = resources["actions"]
            for key in actions:
                if key.startswith("item"):
                    if key not in self._data:
                        self._data[key] = {}
                    self._data[key]["name"] = actions[key]["name"]

    @property
    def actions(self):
        result: list[Action] = []
        for key in self._data:
            result.append(Action(key, self._data[key]["name"], self))

        return result

    def get_features(self, action: Action) -> list[ActionFeature]:
        result = list()

        if action and action.id:
            if action.id in self._data:
                data = self._data[action.id]
                if "currentState" in data and data["currentState"]:
                    result.append(ActionFeature.ON_OFF)

        return result

    def get_state(self, action: Action) -> ActionState:
        if action and action.id:
            if (
                action.id in self._data
                and "currentState" in self._data[action.id]
                and self._data[action.id]["currentState"]
            ):
                return ActionState(int(self._data[action.id]["currentState"]))
        return None

    async def set_state(self, action: Action, state: ActionState) -> None:
        if action and action.id:
            await self._data_provider.write_data(action._resource_path, state)
