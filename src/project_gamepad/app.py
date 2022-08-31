from concurrent.futures import ThreadPoolExecutor, wait
from os import getenv
from typing import Dict, List

from project_gamepad.controllers import (
    ArduinoBoard,
    Gamepad,
    InputController,
    Keyboard,
    Mouse,
)
from project_gamepad.log import get_logger
from project_gamepad.mappers import (
    KeyboardButtonCombinationMapper,
    KeyboardButtonMapper,
    KeyboardDirectionMapper,
    Mapper,
    MouseButtonMapper,
    MouseDirectionMapper,
)

logger = get_logger(__name__)


class App:
    input_devices: Dict[InputController, dict]
    debug: bool
    mappers: List[Mapper]

    def __init__(self, debug: bool = False) -> None:
        self.debug = debug
        self.input_devices = {}

    def attach_mappers(self, mapper: Mapper) -> None:
        self.mappers.append(mapper)
        self.input_devices[mapper.input_device] = {}

    def set_mappers(self, mappers: List[Mapper]) -> None:
        self.mappers = mappers
        for mapper in mappers:
            self.input_devices[mapper.input_device] = {}

    def _monitor_input_device(self, input_device: InputController) -> None:
        while True:
            state = self.input_devices[input_device]
            current_state = input_device.read()
            if state != current_state:
                logger.info(f"State changed of device {input_device}")
                logger.debug("State: %s", current_state)
                self.input_devices[input_device] = current_state
                for mapper in self.mappers:
                    mapper.listen()

    def start_monitors(self) -> None:
        executor = ThreadPoolExecutor(10)
        futures = [
            executor.submit(self._monitor_input_device, device)
            for device in self.input_devices
        ]
        wait(futures)

    def run(self):
        self.start_monitors()


if __name__ == "__main__":
    logger.info("Starting app")
    app = App(debug=getenv("APP_ENV") == "DEV")
    gp = Gamepad()
    kb = Keyboard()
    standard_mouse = Mouse(speed_modifier=10, delay=5, sensitivity=0.01)
    fast_mouse = Mouse(speed_modifier=50, delay=1, sensitivity=0.01)

    modifiers = [
        KeyboardButtonMapper(gp, kb, Gamepad.Key.A, Keyboard.Key.ctrl),
        KeyboardButtonMapper(gp, kb, Gamepad.Key.B, Keyboard.Key.shift),
        KeyboardButtonMapper(gp, kb, Gamepad.Key.X, Keyboard.Key.alt),
    ]

    special = [
        KeyboardButtonMapper(gp, kb, Gamepad.Key.start, Keyboard.Key.enter),
        KeyboardButtonMapper(gp, kb, Gamepad.Key.back, Keyboard.Key.backspace),
        KeyboardButtonMapper(gp, kb, Gamepad.Key.center, Keyboard.Key.menu),
    ]

    d_pad = [
        KeyboardDirectionMapper(
            gp,
            kb,
            Gamepad.Key.H,
            (Keyboard.Key.left, Keyboard.Key.right),
        ),
        KeyboardDirectionMapper(
            gp,
            kb,
            Gamepad.Key.V,
            (Keyboard.Key.up, Keyboard.Key.down),
        ),
    ]

    upper_buttons = [
        KeyboardButtonCombinationMapper(
            gp,
            kb,
            Gamepad.Key.LB,
            [Keyboard.Key.ctrl, Keyboard.Key.f1],
        ),
        KeyboardButtonCombinationMapper(
            gp,
            kb,
            Gamepad.Key.RB,
            [Keyboard.Key.ctrl, Keyboard.Key.f2],
        ),
    ]

    stick = [
        MouseDirectionMapper(
            gp,
            standard_mouse,
            (Gamepad.Key.r_stick_x, Gamepad.Key.r_stick_y),
        ),
        MouseButtonMapper(gp, standard_mouse, Gamepad.Key.r_thumb, Mouse.Key.left),
        MouseDirectionMapper(
            gp,
            fast_mouse,
            (Gamepad.Key.l_stick_x, Gamepad.Key.l_stick_y),
        ),
        MouseButtonMapper(gp, fast_mouse, Gamepad.Key.l_thumb, Mouse.Key.right),
    ]
    gamepad_mappers = modifiers + d_pad + stick + upper_buttons + special
    app.set_mappers(gamepad_mappers)
    # arduino = ArduinoBoard()
    # arduino_mappers = [
    #     KeyboardButtonMapper(
    #         arduino, kb, ArduinoBoard.Key.PIN_2, Keyboard.Key.media_volume_mute
    #     )
    # ]
    # app.set_mappers(arduino_mappers)
    # app.set_mappers(gamepad_mappers + arduino_mappers)

    app.run()
