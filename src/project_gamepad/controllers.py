import enum
import threading
import uuid
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from time import sleep
from typing import Iterable, Optional, Union

from log import get_logger
from PyMata.pymata import PyMata
from pynput.keyboard import Controller as _KeyboardController
from pynput.keyboard import Key as _KeyboardKey
from pynput.mouse import Button as _MouseKey
from pynput.mouse import Controller as _MouseController
from serial import SerialException
from telemetrix import telemetrix

logger = get_logger(__name__)


class MetaEnum(enum.EnumMeta):
    def __contains__(cls, item):
        try:
            cls(item)
        except ValueError:
            return False
        return True


class BaseEnum(enum.Enum, metaclass=MetaEnum):
    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.name)


class KeyController(ABC):
    @abstractmethod
    def press(self):
        ...

    @abstractmethod
    def release(self):
        ...


class InputController(ABC):
    id: uuid.UUID
    state: dict = {}

    class Key(BaseEnum):
        pass

    def __init__(self):
        self.id = uuid.uuid4()
        executor = ThreadPoolExecutor(10)
        executor.submit(self._monitor_controller)

    def read(self):
        return self.state.copy()

    @abstractmethod
    def _monitor_controller(self):
        ...

    def __hash__(self):
        return hash(self.id)

    def __str__(self):
        return f"{self.__class__.__name__}({self.id})"


class Keyboard(_KeyboardController, KeyController):

    Key = _KeyboardKey

    def __init__(self) -> None:
        super().__init__()
        self.Key = Union[_KeyboardKey, str]


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
            name=str(self), target=self._monitor_controller, args=()
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


class Gamepad(InputController):
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
        super().__init__()

    def _monitor_controller(self) -> None:

        while True:
            try:
                from inputs import InputEvent, get_gamepad

                events: Iterable[InputEvent] = get_gamepad()
                for ev in events:
                    logger.debug("Event: %s:%s:%s", ev.ev_type, ev.code, ev.state)
                    if ev.code in Gamepad.Key:
                        state = ev.state
                        if ev.code in self.TO_NORMALIZE:
                            state = round(ev.state / self.TO_NORMALIZE[ev.code], 2)
                        self.state[Gamepad.Key(ev.code)] = state
            except Exception as e:
                logger.error(str(e))


class ArduinoBoard(InputController):
    port: Optional[str]
    board: Optional[PyMata]

    class Key(BaseEnum):
        PIN_2 = 2

    def __init__(self):
        self.state = {k: 0 for k in ArduinoBoard.Key}
        self.board = None
        super().__init__()

    def _monitor_controller(self) -> None:
        while True:
            self.setup_board()

    def setup_board(self):
        while self.board is None:
            logger.info("Looking for Arduino boards...")
            try:
                self.board = telemetrix.Telemetrix()
                for key in ArduinoBoard.Key:
                    self.board.set_pin_mode_digital_input(
                        key.value, callback=self._callback
                    )
            except SerialException as ex:
                logger.error(str(ex))
            except Exception as ex:
                logger.error(str(ex))
                self.board.shutdown()
                self.board = None
            sleep(1)

    def _callback(self, data):
        self.state[ArduinoBoard.Key(data[1])] = data[2]
