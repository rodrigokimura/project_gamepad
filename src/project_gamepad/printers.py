from abc import ABC, abstractmethod

from colorama import Fore, Style

from project_gamepad.controllers import Gamepad


class Printer(ABC):
    @abstractmethod
    def print(self):
        ...


class GamepadColoredPrinter(Printer):
    def __init__(self, gp: Gamepad) -> None:
        self.gp = gp

    def print(self) -> None:

        green = lambda s: Fore.GREEN + s + Style.RESET_ALL
        red = lambda s: Fore.RED + s + Style.RESET_ALL
        dim = lambda s: Style.DIM + s + Style.RESET_ALL
        noop = lambda s: s
        green_or_dim = lambda s, v: green(s) if v else dim(s)

        lt = green_or_dim("___", self.gp.state[Gamepad.Key.LT])
        rt = green_or_dim("___", self.gp.state[Gamepad.Key.RT])

        lb = green_or_dim("---", self.gp.state[Gamepad.Key.LB])
        rb = green_or_dim("---", self.gp.state[Gamepad.Key.RB])

        up = (green if self.gp.state[Gamepad.Key.V] == -1 else dim)("↑")
        down = (green if self.gp.state[Gamepad.Key.V] == 1 else dim)("↓")
        left = (green if self.gp.state[Gamepad.Key.H] == -1 else dim)("←")
        right = (green if self.gp.state[Gamepad.Key.H] == 1 else dim)("→")

        a = green_or_dim("A", self.gp.state[Gamepad.Key.A])
        b = green_or_dim("B", self.gp.state[Gamepad.Key.B])
        x = green_or_dim("X", self.gp.state[Gamepad.Key.X])
        y = green_or_dim("Y", self.gp.state[Gamepad.Key.Y])

        d_pad = [f" {up} ", f"{left} {right}", f" {down} "]
        buttons = [f" {y} ", f"{x} {b}", f" {a} "]

        start = green_or_dim("-", self.gp.state[Gamepad.Key.start])
        back = green_or_dim("-", self.gp.state[Gamepad.Key.back])
        center = green_or_dim("*", self.gp.state[Gamepad.Key.center])

        # os.system("cls||clear")

        print(f"{lt}{' ' * 7}{rt}")
        print(f"{lb}{' ' * 7}{rb}")
        print(
            "\n".join(
                "".join(t)
                for t in zip(
                    d_pad, [f" {back} {center} {start} ", " " * 7, " " * 7], buttons
                )
            )
        )
