from os import getenv
from threading import Thread
from tkinter import Tk, ttk
from typing import Dict, List

import chime

from project_gamepad.controllers import (
    Gamepad,
    InputController,
    Keyboard,
    MonitorableDevice,
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
    stopped: bool
    mappers: List[Mapper]
    devices_to_stop_monitoring: List[MonitorableDevice] = []

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
        while self.stopped is False:
            state = self.input_devices[input_device]
            current_state = input_device.read()
            if state != current_state:
                logger.info(f"State changed of device {input_device}")
                logger.debug("State: %s", current_state)
                self.input_devices[input_device] = current_state
                for mapper in self.mappers:
                    mapper.listen()

    def run(self) -> None:
        self.stopped = False

        chime.success()
        input_device = next(iter(self.input_devices))
        self._monitor_input_device(input_device)

    def stop(self) -> None:
        self.stopped = True

    def destroy(self) -> None:
        self.stop()
        for input_device in self.input_devices:
            input_device.stop()
        for device in self.devices_to_stop_monitoring:
            device.stop_monitoring()


def create_app() -> App:
    app = App(debug=getenv("APP_ENV") == "DEV")
    gp = Gamepad()
    kb = Keyboard()
    standard_mouse = Mouse(speed_modifier=10, delay=5, sensitivity=0.01)
    fast_mouse = Mouse(speed_modifier=50, delay=1, sensitivity=0.01)

    app.devices_to_stop_monitoring = [standard_mouse, fast_mouse]

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

    app.set_mappers(gamepad_mappers)
    return app


def start_app(app: App):
    main_thread = Thread(target=lambda: app.run(), name="start_app")
    main_thread.start()


def stop_app(app: App):
    app.stop()


def destroy_app(app: App, tk: Tk):
    app.destroy()
    tk.destroy()


def main():
    app = create_app()

    root = Tk()

    style = ttk.Style(root)
    style.theme_use("clam")

    frm = ttk.Frame(root, padding=10)
    frm.pack()

    ttk.Button(
        frm,
        text="Start",
        command=lambda: start_app(app),
    ).grid(column=0, row=1)
    ttk.Button(
        frm,
        text="Exit",
        command=lambda: destroy_app(app, root),
    ).grid(column=0, row=4)

    root.mainloop()


if __name__ == "__main__":
    logger.info("Starting app")
    main()
