from abc import ABC, abstractmethod
from typing import Collection

from controllers import Gamepad


class Event(ABC):
    gamepad: Gamepad
    keys: Collection[Gamepad.Key]
    @abstractmethod
    def is_set(self) -> bool:
        ...


class OnKeyPress(Event):

    def __init__(self, gamepad, keys) -> None:
        self.gamepad = gamepad
        self.keys = keys

    def is_set(self) -> bool:
        return all(
            [
                self.gamepad.status[k] == 1
                for k in self.keys
            ]
        )
