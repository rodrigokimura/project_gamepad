from abc import ABC, abstractmethod
from typing import Collection, Tuple

from project_gamepad.commands import MovePointer, PressKey, ReleaseKey, StopPointer
from project_gamepad.controllers import Gamepad, Keyboard, Mouse
from project_gamepad.events import (
    OnKeyPress,
    OnKeyRelease,
    OnKeyStateChange,
    OnStickMove,
    OnStickStop,
)
from project_gamepad.listeners import Listener


class KeyboardMapper(ABC):

    gp: Gamepad
    kb: Keyboard
    _listeners: Collection[Listener]

    @abstractmethod
    def __init__(self, gp: Gamepad, kb: Keyboard) -> None:
        self.gp = gp
        self.kb = kb

    def listen(self) -> None:
        for listener in self._listeners:
            listener.listen()


class MouseMapper(ABC):

    gp: Gamepad
    m: Mouse
    _listeners: Collection[Listener]

    @abstractmethod
    def __init__(self, gp: Gamepad, m: Mouse) -> None:
        self.gp = gp
        self.m = m

    def listen(self) -> None:
        for listener in self._listeners:
            listener.listen()


class KeyboardButtonMapper(KeyboardMapper):
    def __init__(
        self, gp: Gamepad, kb: Keyboard, gp_key: Gamepad.Key, kb_key: Keyboard.Key
    ) -> None:
        super().__init__(gp, kb)
        self._listeners = [
            Listener(OnKeyPress(gp, [gp_key]), [PressKey(kb, kb_key)]),
            Listener(OnKeyRelease(gp, [gp_key]), [ReleaseKey(kb, kb_key)]),
        ]


class KeyboardButtonCombinationMapper(KeyboardMapper):
    def __init__(
        self,
        gp: Gamepad,
        kb: Keyboard,
        gp_key: Gamepad.Key,
        kb_keys: Collection[Keyboard.Key],
    ) -> None:
        super().__init__(gp, kb)
        self._listeners = [
            Listener(OnKeyPress(gp, [gp_key]), [PressKey(kb, key) for key in kb_keys]),
            Listener(
                OnKeyRelease(gp, [gp_key]), [ReleaseKey(kb, key) for key in kb_keys]
            ),
        ]


class KeyboardDirectionMapper(KeyboardMapper):
    def __init__(
        self,
        gp: Gamepad,
        kb: Keyboard,
        gp_key: Gamepad.Key,
        kb_keys: Tuple[Keyboard.Key, Keyboard.Key],
    ) -> None:
        super().__init__(gp, kb)
        self._listeners = [
            Listener(OnKeyStateChange(gp, [gp_key], -1), [PressKey(kb, kb_keys[0])]),
            Listener(OnKeyStateChange(gp, [gp_key], 1), [PressKey(kb, kb_keys[1])]),
            Listener(
                OnKeyStateChange(gp, [gp_key], 0),
                [ReleaseKey(kb, kb_keys[0]), ReleaseKey(kb, kb_keys[1])],
            ),
        ]


class MouseButtonMapper(MouseMapper):
    def __init__(
        self, gp: Gamepad, m: Mouse, gp_key: Gamepad.Key, m_key: Mouse.Key
    ) -> None:
        super().__init__(gp, m)
        self._listeners = [
            Listener(OnKeyPress(gp, [gp_key]), [PressKey(m, m_key)]),
            Listener(OnKeyRelease(gp, [gp_key]), [ReleaseKey(m, m_key)]),
        ]


class MouseDirectionMapper(MouseMapper):
    def __init__(
        self, gp: Gamepad, m: Mouse, stick_keys: Tuple[Gamepad.Key, Gamepad.Key]
    ) -> None:
        super().__init__(gp, m)
        self._listeners = [
            Listener(OnStickMove(gp, (stick_keys[0], stick_keys[1])), [MovePointer(m)]),
            Listener(OnStickStop(gp, (stick_keys[0], stick_keys[1])), [StopPointer(m)]),
        ]
