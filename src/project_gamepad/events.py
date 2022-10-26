from abc import ABC, abstractmethod
from typing import Any, Collection, Dict, Tuple

from project_gamepad.controllers import InputController


class Event(ABC):
    input_device: InputController
    keys: Collection[InputController.Key]
    context: Dict[str, Any]

    @abstractmethod
    def is_set(self) -> bool:
        ...


class OnStickMove(Event):

    context = {}

    def __init__(
        self,
        input_device: InputController,
        axis_keys: Tuple[InputController.Key, InputController.Key],
    ) -> None:
        self.input_device = input_device
        self.keys = axis_keys

    def is_set(self) -> bool:
        self.context = {
            "x": self.input_device.state[self.keys[0]],
            "y": self.input_device.state[self.keys[1]],
        }
        return (
            abs(self.input_device.state[self.keys[0]]) > 0.0
            and abs(self.input_device.state[self.keys[1]]) > 0.0
        )


class OnStickStop(Event):

    context = {}

    def __init__(
        self,
        input_device: InputController,
        axis_keys: Tuple[InputController.Key, InputController.Key],
    ) -> None:
        self.input_device = input_device
        self.keys = axis_keys

    def is_set(self) -> bool:
        return (
            abs(self.input_device.state[self.keys[0]]) == 0.0
            and abs(self.input_device.state[self.keys[1]]) == 0.0
        )


class OnKeyStateChange(Event):

    context = {}

    def __init__(self, input_device, keys, state) -> None:
        self.input_device = input_device
        self.keys = keys
        self.state = state

    def is_set(self) -> bool:
        return all([self.input_device.state[k] == self.state for k in self.keys])


class OnKeyPress(OnKeyStateChange):
    def __init__(self, input_device, keys) -> None:
        state = 1
        super().__init__(input_device, keys, state)


class OnKeyRelease(OnKeyStateChange):
    def __init__(self, input_device, keys) -> None:
        state = 0
        super().__init__(input_device, keys, state)


class OnRotation(Event):
    context = {}

    def __init__(self, input_device, dt_key, clk_key) -> None:
        self.input_device = input_device
        self.dt_key = dt_key
        self.clk_key = clk_key

    def is_set(self) -> bool:
        return self.input_device.state[self.clk_key] == 1


class OnClockWiseRotation(OnRotation):
    def is_set(self) -> bool:
        clk = self.input_device.state[self.clk_key]
        dt = self.input_device.state[self.dt_key]
        return super().is_set() and clk == dt


class OnCounterClockWiseRotation(OnRotation):
    def is_set(self) -> bool:
        clk = self.input_device.state[self.clk_key]
        dt = self.input_device.state[self.dt_key]
        return super().is_set() and clk != dt
