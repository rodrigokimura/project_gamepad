import asyncio
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
    RotaryEncoderMapper,
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

    async def _monitor_input_device(self, input_device: InputController) -> None:
        while True:
            state = self.input_devices[input_device]
            current_state = input_device.read()
            if state != current_state:
                logger.info(f"State changed of device {input_device}")
                logger.debug("State: %s", current_state)
                self.input_devices[input_device] = current_state
                for mapper in self.mappers:
                    mapper.listen()

    def run(self):
        import chime

        chime.success()
        loop = asyncio.get_event_loop()
        for device in self.input_devices:
            loop.create_task(self._monitor_input_device(device))
        loop.run_forever()


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
            [Keyboard.Key.ctrl, Keyboard.Key.cmd, Keyboard.Key.f1],
        ),
        KeyboardButtonCombinationMapper(
            gp,
            kb,
            Gamepad.Key.RB,
            [Keyboard.Key.ctrl, Keyboard.Key.cmd, Keyboard.Key.f2],
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

    if getenv("DEVICE", "").lower() == "arduino":
        arduino = ArduinoBoard()
        arduino_mappers = [
            KeyboardButtonMapper(
                arduino, kb, ArduinoBoard.Key.PIN_2, Keyboard.Key.media_volume_mute
            ),
            # KeyboardButtonMapper(
            #     arduino, kb, ArduinoBoard.Key.PIN_8, Keyboard.Key.media_volume_mute
            # ),
            # RotaryEncoderMapper(
            #     arduino, kb, ArduinoBoard.Key.PIN_10, ArduinoBoard.Key.PIN_11, Keyboard.Key.media_volume_up,Keyboard.Key.media_volume_down
            # ),
        ]
        app.set_mappers(arduino_mappers)
    elif getenv("DEVICE", "").lower() == "gamepad":
        app.set_mappers(gamepad_mappers)
    else:
        raise NotImplementedError("Device not implemented")

    app.run()
