from abc import ABC, abstractmethod
from typing import Any, Collection, Dict, Tuple

from project_gamepad.controllers import Gamepad


class Event(ABC):
    gamepad: Gamepad
    keys: Collection[Gamepad.Key]
    context: Dict[str, Any]

    @abstractmethod
    def is_set(self) -> bool:
        ...


class OnStickMove(Event):

    context = {}

    def __init__(
        self, gamepad: Gamepad, axis_keys: Tuple[Gamepad.Key, Gamepad.Key]
    ) -> None:
        self.gamepad = gamepad
        self.keys = axis_keys

    def is_set(self) -> bool:
        self.context = {
            "x": self.gamepad.state[self.keys[0]],
            "y": self.gamepad.state[self.keys[1]],
        }
        return (
            abs(self.gamepad.state[self.keys[0]]) > 0.0
            and abs(self.gamepad.state[self.keys[1]]) > 0.0
        )


class OnStickStop(Event):

    context = {}

    def __init__(
        self, gamepad: Gamepad, axis_keys: Tuple[Gamepad.Key, Gamepad.Key]
    ) -> None:
        self.gamepad = gamepad
        self.keys = axis_keys

    def is_set(self) -> bool:
        return (
            abs(self.gamepad.state[self.keys[0]]) == 0.0
            and abs(self.gamepad.state[self.keys[1]]) == 0.0
        )


class OnKeyStateChange(Event):

    context = {}

    def __init__(self, gamepad, keys, state) -> None:
        self.gamepad = gamepad
        self.keys = keys
        self.state = state

    def is_set(self) -> bool:
        return all([self.gamepad.state[k] == self.state for k in self.keys])


class OnKeyPress(OnKeyStateChange):
    def __init__(self, gamepad, keys) -> None:
        state = 1
        super().__init__(gamepad, keys, state)


class OnKeyRelease(OnKeyStateChange):
    def __init__(self, gamepad, keys) -> None:
        state = 0
        super().__init__(gamepad, keys, state)
