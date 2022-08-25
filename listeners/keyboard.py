from controllers import KeyboardController, Gamepad
from mappers import binary_mapper, ternary_mapper

from pynput.keyboard import Key


def on_d_pad(gp: Gamepad, kb: KeyboardController):
    ternary_mapper(gp, kb, Gamepad.Key.H, (Key.right, Key.left))
    ternary_mapper(gp, kb, Gamepad.Key.V, (Key.down, Key.up))


def on_start(gp: Gamepad, kb: KeyboardController):
    binary_mapper(gp, kb, Gamepad.Key.start, Key.enter)


def on_back(gp: Gamepad, kb: KeyboardController):
    binary_mapper(gp, kb, Gamepad.Key.back, Key.backspace)


def on_a(gp: Gamepad, kb: KeyboardController):
    binary_mapper(gp, kb, Gamepad.Key.A, Key.ctrl)


def on_x(gp: Gamepad, kb: KeyboardController):
    binary_mapper(gp, kb, Gamepad.Key.X, Key.shift)


def on_b(gp: Gamepad, kb: KeyboardController):
    binary_mapper(gp, kb, Gamepad.Key.B, Key.alt)


all_listeners = [f for f in globals().values() if callable(f) and str(f.__name__).startswith('on_')]
