import enum
import threading
import uuid
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from time import sleep
from typing import Iterable, Union

from project_gamepad.log import get_logger
from project_gamepad.wrappers.output_devices import (
    KeyboardController,
    KeyboardKey,
    MouseController,
    MouseKey,
)

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
    monitoring: bool = True
    state: dict = {}

    class Key(BaseEnum):
        pass

    def __init__(self):
        self.id = uuid.uuid4()
        self.executor = ThreadPoolExecutor(10)
        self.executor.submit(self.monitor_controller)

    def read(self):
        return self.state.copy()

    @abstractmethod
    def _monitor_controller(self):
        ...

    def monitor_controller(self):
        while self.monitoring:
            self._monitor_controller()

    def stop(self):
        self.monitoring = False
        self.executor.shutdown(wait=False)

    def __hash__(self):
        return hash(self.id)

    def __str__(self):
        return f"{self.__class__.__name__}({self.id})"


class Keyboard(KeyboardController, KeyController):

    Key = KeyboardKey

    def __init__(self) -> None:
        super().__init__()
        self.Key = Union[KeyboardKey, str]


class MonitorableDevice:
    monitoring: bool = True

    def stop_monitoring(self):
        self.monitoring = False


class Mouse(MouseController, KeyController, MonitorableDevice):

    Key = MouseKey

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
        while self.monitoring:
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
