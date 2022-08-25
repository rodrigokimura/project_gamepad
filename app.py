from controllers import Gamepad, Keyboard, Mouse
from mappers import (
    KeyboardButtonCombinationMapper,
    KeyboardButtonMapper,
    KeyboardDirectionMapper,
    MouseButtonMapper,
    MouseDirectionMapper,
)
from printers import GamepadColoredPrinter


class App:
    gp = Gamepad()
    printer = GamepadColoredPrinter(gp)
    kb = Keyboard()
    standard_mouse = Mouse(speed_modifier=10, delay=5, sensitivity=0.01)
    fast_mouse = Mouse(speed_modifier=50, delay=1, sensitivity=0.01)

    state = {}

    print_gamepad = True

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
            gp, kb, Gamepad.Key.H, (Keyboard.Key.left, Keyboard.Key.right)
        ),
        KeyboardDirectionMapper(
            gp, kb, Gamepad.Key.V, (Keyboard.Key.up, Keyboard.Key.down)
        ),
    ]

    upper_buttons = [
        KeyboardButtonCombinationMapper(
            gp, kb, Gamepad.Key.LB, [Keyboard.Key.ctrl, Keyboard.Key.f1]
        ),
        KeyboardButtonCombinationMapper(
            gp, kb, Gamepad.Key.RB, [Keyboard.Key.ctrl, Keyboard.Key.f2]
        ),
    ]

    stick = [
        MouseDirectionMapper(
            gp, standard_mouse, (Gamepad.Key.r_stick_x, Gamepad.Key.r_stick_y)
        ),
        MouseButtonMapper(gp, standard_mouse, Gamepad.Key.r_thumb, Mouse.Key.left),
        MouseDirectionMapper(
            gp, fast_mouse, (Gamepad.Key.l_stick_x, Gamepad.Key.l_stick_y)
        ),
        MouseButtonMapper(gp, fast_mouse, Gamepad.Key.l_thumb, Mouse.Key.right),
    ]

    mappers = modifiers + d_pad + stick + upper_buttons

    def run(self):
        while True:
            current_state = self.gp.read()
            if self.state != current_state:
                self.state = current_state
                if self.print_gamepad:  # TODO: use logging
                    self.printer.print()
                for listener in self.mappers:
                    listener.listen()


if __name__ == "__main__":
    app = App()
    app.run()
