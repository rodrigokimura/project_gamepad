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
    KeyboardButtonDelayMapper,
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

    def run(self):
        while True:
            for device, state in self.input_devices.items():
                current_state = device.read()
                if state != current_state:
                    logger.info(f"State changed of device {device}")
                    logger.debug("State: %s", current_state)
                    self.input_devices[device] = current_state
                    for mapper in self.mappers:
                        mapper.listen()


if __name__ == "__main__":
    logger.info("Starting app")
    app = App(debug=getenv("APP_ENV") == "DEV")
    gp = Gamepad()
    arduino = ArduinoBoard()
    kb = Keyboard()
    standard_mouse = Mouse(speed_modifier=10, delay=5, sensitivity=0.01)
    fast_mouse = Mouse(speed_modifier=50, delay=1, sensitivity=0.01)
    arduino_mappers = [
        KeyboardButtonMapper(
            arduino, kb, ArduinoBoard.Key.PIN_2, Keyboard.Key.media_volume_mute
        )
    ]
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
    app.set_mappers(
        modifiers + d_pad + stick + upper_buttons + special + arduino_mappers
    )

    app.run()
