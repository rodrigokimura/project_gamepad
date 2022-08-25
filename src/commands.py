import enum
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict

from controllers import Keyboard, KeyController, Mouse


class Command(ABC):
    @abstractmethod
    def run(self, context: Dict[str, Any]) -> None:
        ...


class MovePointer(Command):
    def __init__(self, mouse: Mouse):
        self.mouse = mouse

    def run(self, context):
        self.mouse.speed_x = context["x"]
        self.mouse.speed_y = context["y"]
        self.mouse.start()


class StopPointer(Command):
    def __init__(self, mouse: Mouse):
        self.mouse = mouse

    def run(self, context):
        self.mouse.speed_x = 0
        self.mouse.speed_y = 0
        self.mouse.stop()


class KeyCommand(Command):
    def __init__(self, command: Callable[[Keyboard.Key], None], key: Keyboard.Key):
        self.command = command
        self.key = key

    def run(self, context):
        self.command(self.key)


class PressKey(KeyCommand):
    def __init__(self, controller: KeyController, key: enum.Enum):
        super().__init__(controller.press, key)


class ReleaseKey(KeyCommand):
    def __init__(self, controller: KeyController, key: enum.Enum):
        super().__init__(controller.release, key)
