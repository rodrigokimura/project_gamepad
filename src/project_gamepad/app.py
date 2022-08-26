from os import getenv

from project_gamepad.controllers import Gamepad, Keyboard, Mouse
from project_gamepad.log import get_logger
from project_gamepad.mappers import (
    KeyboardButtonCombinationMapper,
    KeyboardButtonMapper,
    KeyboardDirectionMapper,
    MouseButtonMapper,
    MouseDirectionMapper,
)

logger = get_logger(__name__)


class App:
    gp: Gamepad
    debug: bool
    state = {}

    def __init__(self, debug: bool = False) -> None:
        self.debug = debug
        self.gp = Gamepad()
        kb = Keyboard()
        standard_mouse = Mouse(speed_modifier=10, delay=5, sensitivity=0.01)
        fast_mouse = Mouse(speed_modifier=50, delay=1, sensitivity=0.01)
        modifiers = [
            KeyboardButtonMapper(self.gp, kb, Gamepad.Key.A, Keyboard.Key.ctrl),
            KeyboardButtonMapper(self.gp, kb, Gamepad.Key.B, Keyboard.Key.shift),
            KeyboardButtonMapper(self.gp, kb, Gamepad.Key.X, Keyboard.Key.alt),
        ]

        special = [
            KeyboardButtonMapper(self.gp, kb, Gamepad.Key.start, Keyboard.Key.enter),
            KeyboardButtonMapper(self.gp, kb, Gamepad.Key.back, Keyboard.Key.backspace),
            KeyboardButtonMapper(self.gp, kb, Gamepad.Key.center, Keyboard.Key.menu),
        ]

        d_pad = [
            KeyboardDirectionMapper(
                self.gp, kb, Gamepad.Key.H, (Keyboard.Key.left, Keyboard.Key.right)
            ),
            KeyboardDirectionMapper(
                self.gp, kb, Gamepad.Key.V, (Keyboard.Key.up, Keyboard.Key.down)
            ),
        ]

        upper_buttons = [
            KeyboardButtonCombinationMapper(
                self.gp, kb, Gamepad.Key.LB, [Keyboard.Key.ctrl, Keyboard.Key.f1]
            ),
            KeyboardButtonCombinationMapper(
                self.gp, kb, Gamepad.Key.RB, [Keyboard.Key.ctrl, Keyboard.Key.f2]
            ),
        ]

        stick = [
            MouseDirectionMapper(
                self.gp, standard_mouse, (Gamepad.Key.r_stick_x, Gamepad.Key.r_stick_y)
            ),
            MouseButtonMapper(
                self.gp, standard_mouse, Gamepad.Key.r_thumb, Mouse.Key.left
            ),
            MouseDirectionMapper(
                self.gp, fast_mouse, (Gamepad.Key.l_stick_x, Gamepad.Key.l_stick_y)
            ),
            MouseButtonMapper(
                self.gp, fast_mouse, Gamepad.Key.l_thumb, Mouse.Key.right
            ),
        ]
        self.mappers = modifiers + d_pad + stick + upper_buttons + special

    def run(self):
        while True:
            current_state = self.gp.read()
            if self.state != current_state:
                logger.info("State changed")
                logger.debug("State: %s", current_state)
                self.state = current_state
                for listener in self.mappers:
                    listener.listen()


if __name__ == "__main__":
    logger.info("Starting app")
    if getenv("APP_ENV") == "DEV":
        App(debug=True).run()
    else:
        App().run()
