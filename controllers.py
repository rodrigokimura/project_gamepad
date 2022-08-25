import enum
import threading
from abc import ABC, abstractmethod
from time import sleep

from inputs import get_gamepad
from pynput.keyboard import Controller as _KeyboardController
from pynput.keyboard import Key as _KeyboardKey
from pynput.mouse import Button as _MouseKey
from pynput.mouse import Controller as _MouseController


class KeyController(ABC):
    @abstractmethod
    def press(self):
        ...

    @abstractmethod
    def release(self):
        ...


class Keyboard(_KeyboardController, KeyController):

    Key = _KeyboardKey

    def __init__(self) -> None:
        super().__init__()
        self.Key = _KeyboardKey


class Mouse(_MouseController, KeyController):

    Key = _MouseKey

    def __init__(
        self, sensitivity: float = 0.01, delay: int = 5, speed_modifier: int = 20
    ) -> None:
        super().__init__()
        self.sensitivity = sensitivity
        self.delay = delay
        self.speed_modifier = speed_modifier
        self.speed_x = 0
        self.speed_y = 0
        self._stopped = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_controller, args=()
        )
        self._monitor_thread.daemon = True
        self._monitor_thread.start()

    def stop(self):
        self._stopped = True

    def start(self):
        self._stopped = False

    def move(self):
        super().move(
            self.speed_x * self.speed_modifier,
            self.speed_y * self.speed_modifier,
        )

    def _monitor_controller(self) -> None:
        while True:
            if self.delay:
                sleep(self.delay / 1000)
            if not self._stopped:
                self.move()


class MetaEnum(enum.EnumMeta):
    def __contains__(cls, item):
        try:
            cls(item)
        except ValueError:
            return False
        return True


class BaseEnum(enum.Enum, metaclass=MetaEnum):
    pass


class Gamepad:
    class Key(BaseEnum):
        A = "BTN_SOUTH"
        B = "BTN_EAST"
        X = "BTN_NORTH"
        Y = "BTN_WEST"
        H = "ABS_HAT0X"
        V = "ABS_HAT0Y"
        LB = "BTN_TL"
        RB = "BTN_TR"
        LT = "ABS_Z"
        RT = "ABS_RZ"
        start = "BTN_START"
        back = "BTN_SELECT"
        center = "BTN_MODE"
        l_stick_x = "ABS_X"
        l_stick_y = "ABS_Y"
        r_stick_x = "ABS_RX"
        r_stick_y = "ABS_RY"
        l_thumb = "BTN_THUMBL"
        r_thumb = "BTN_THUMBR"

    MAX_TRIG_VAL = 2**8
    MAX_JOY_VAL = 2**15
    state = {k: 0 for k in Key}
    TO_NORMALIZE = {
        "ABS_X": MAX_JOY_VAL,
        "ABS_Y": MAX_JOY_VAL,
        "ABS_RX": MAX_JOY_VAL,
        "ABS_RY": MAX_JOY_VAL,
        "ABS_Z": MAX_TRIG_VAL,
        "ABS_RZ": MAX_TRIG_VAL,
    }

    def __init__(self):
        self.state = {k: 0 for k in Gamepad.Key}
        self._monitor_thread = threading.Thread(
            target=self._monitor_controller, args=(False, 2)
        )
        self._monitor_thread.daemon = True
        self._monitor_thread.start()

    def read(self):
        d_pad = [self.state[Gamepad.Key.H], self.state[Gamepad.Key.V]]
        buttons = [
            self.state[Gamepad.Key.A],
            self.state[Gamepad.Key.B],
            self.state[Gamepad.Key.X],
            self.state[Gamepad.Key.Y],
        ]
        special = [
            self.state[Gamepad.Key.back],
            self.state[Gamepad.Key.start],
            self.state[Gamepad.Key.center],
        ]
        sticks = [
            (
                self.state[Gamepad.Key.l_stick_x],
                self.state[Gamepad.Key.l_stick_y],
                self.state[Gamepad.Key.l_thumb],
            ),
            (
                self.state[Gamepad.Key.r_stick_x],
                self.state[Gamepad.Key.r_stick_y],
                self.state[Gamepad.Key.r_thumb],
            ),
        ]
        upper = [
            self.state[Gamepad.Key.LB],
            self.state[Gamepad.Key.RB],
            self.state[Gamepad.Key.LT],
            self.state[Gamepad.Key.RT],
        ]
        d = locals()
        del d["self"]
        return d

    def _monitor_controller(self, print_ev=False, stick_precision=1) -> None:

        while True:
            events = get_gamepad()
            for ev in events:
                if print_ev:  # TODO: convert this to logging
                    print(ev.code)
                if ev.code in Gamepad.Key:
                    state = ev.state
                    if ev.code in self.TO_NORMALIZE:
                        state = round(
                            ev.state / self.TO_NORMALIZE[ev.code], stick_precision
                        )
                    self.state[Gamepad.Key(ev.code)] = state
