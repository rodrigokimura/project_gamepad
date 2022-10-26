from abc import ABC, abstractmethod
from typing import Collection, Tuple

from project_gamepad.commands import (
    MovePointer,
    PressKey,
    ReleaseKey,
    Sleep,
    StopPointer,
)
from project_gamepad.controllers import (
    ArduinoBoard,
    Gamepad,
    InputController,
    Keyboard,
    Mouse,
)
from project_gamepad.events import (
    OnClockWiseRotation,
    OnCounterClockWiseRotation,
    OnKeyPress,
    OnKeyRelease,
    OnKeyStateChange,
    OnStickMove,
    OnStickStop,
)
from project_gamepad.listeners import Listener


class Mapper(ABC):

    input_device: InputController
    _listeners: Collection[Listener]

    def listen(self) -> None:
        for listener in self._listeners:
            listener.listen()


class KeyboardMapper(Mapper):

    input_device: Gamepad
    kb: Keyboard
    _listeners: Collection[Listener]

    @abstractmethod
    def __init__(self, input_device: Gamepad, kb: Keyboard) -> None:
        self.input_device = input_device
        self.kb = kb


class MouseMapper(Mapper):

    input_device: Gamepad
    m: Mouse
    _listeners: Collection[Listener]

    @abstractmethod
    def __init__(self, input_device: Gamepad, m: Mouse) -> None:
        self.input_device = input_device
        self.m = m


class KeyboardButtonMapper(KeyboardMapper):
    def __init__(
        self,
        input_device: Gamepad,
        kb: Keyboard,
        gp_key: Gamepad.Key,
        kb_key: Keyboard.Key,
    ) -> None:
        super().__init__(input_device, kb)
        self._listeners = [
            Listener(OnKeyPress(input_device, [gp_key]), [PressKey(kb, kb_key)]),
            Listener(OnKeyRelease(input_device, [gp_key]), [ReleaseKey(kb, kb_key)]),
        ]


class RotaryEncoderMapper(KeyboardMapper):
    def __init__(
        self,
        input_device: ArduinoBoard,
        kb: Keyboard,
        dt_pin: ArduinoBoard.Key,
        clk_pin: ArduinoBoard.Key,
        cw_key: Keyboard.Key,
        ccw_key: Keyboard.Key,
    ) -> None:
        DELAY = 0.5
        super().__init__(input_device, kb)
        self._listeners = [
            Listener(
                OnClockWiseRotation(input_device, dt_pin, clk_pin),
                [PressKey(kb, cw_key), Sleep(DELAY), ReleaseKey(kb, cw_key)],
            ),
            Listener(
                OnCounterClockWiseRotation(input_device, dt_pin, clk_pin),
                [PressKey(kb, ccw_key), Sleep(DELAY), ReleaseKey(kb, ccw_key)],
            ),
        ]


class KeyboardButtonDelayMapper(KeyboardMapper):
    def __init__(
        self,
        input_device: Gamepad,
        kb: Keyboard,
        gp_key: Gamepad.Key,
        kb_key: Keyboard.Key,
    ) -> None:
        super().__init__(input_device, kb)
        self._listeners = [
            Listener(
                OnKeyPress(input_device, [gp_key]),
                [PressKey(kb, kb_key), Sleep(1), ReleaseKey(kb, kb_key)],
            ),
        ]


class KeyboardButtonCombinationMapper(KeyboardMapper):
    def __init__(
        self,
        input_device: Gamepad,
        kb: Keyboard,
        gp_key: Gamepad.Key,
        kb_keys: Collection[Keyboard.Key],
    ) -> None:
        super().__init__(input_device, kb)
        self._listeners = [
            Listener(
                OnKeyPress(input_device, [gp_key]),
                [PressKey(kb, key) for key in kb_keys],
            ),
            Listener(
                OnKeyRelease(input_device, [gp_key]),
                [ReleaseKey(kb, key) for key in kb_keys],
            ),
        ]


class KeyboardDirectionMapper(KeyboardMapper):
    def __init__(
        self,
        input_device: Gamepad,
        kb: Keyboard,
        gp_key: Gamepad.Key,
        kb_keys: Tuple[Keyboard.Key, Keyboard.Key],
    ) -> None:
        super().__init__(input_device, kb)
        self._listeners = [
            Listener(
                OnKeyStateChange(input_device, [gp_key], -1), [PressKey(kb, kb_keys[0])]
            ),
            Listener(
                OnKeyStateChange(input_device, [gp_key], 1), [PressKey(kb, kb_keys[1])]
            ),
            Listener(
                OnKeyStateChange(input_device, [gp_key], 0),
                [ReleaseKey(kb, kb_keys[0]), ReleaseKey(kb, kb_keys[1])],
            ),
        ]


class MouseButtonMapper(MouseMapper):
    def __init__(
        self, input_device: Gamepad, m: Mouse, gp_key: Gamepad.Key, m_key: Mouse.Key
    ) -> None:
        super().__init__(input_device, m)
        self._listeners = [
            Listener(OnKeyPress(input_device, [gp_key]), [PressKey(m, m_key)]),
            Listener(OnKeyRelease(input_device, [gp_key]), [ReleaseKey(m, m_key)]),
        ]


class MouseDirectionMapper(MouseMapper):
    def __init__(
        self,
        input_device: Gamepad,
        m: Mouse,
        stick_keys: Tuple[Gamepad.Key, Gamepad.Key],
    ) -> None:
        super().__init__(input_device, m)
        self._listeners = [
            Listener(
                OnStickMove(input_device, (stick_keys[0], stick_keys[1])),
                [MovePointer(m)],
            ),
            Listener(
                OnStickStop(input_device, (stick_keys[0], stick_keys[1])),
                [StopPointer(m)],
            ),
        ]
