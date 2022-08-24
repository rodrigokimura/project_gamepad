from controllers import KeyboardController, LogitechController
from mappers import binary_mapper, ternary_mapper

from pynput.keyboard import Key


def on_d_pad(lc: LogitechController, kb: KeyboardController):
    ternary_mapper(lc, kb, 'H', (Key.right, Key.left))
    ternary_mapper(lc, kb, 'V', (Key.down, Key.up))


def on_start(lc: LogitechController, kb: KeyboardController):
    binary_mapper(lc, kb, 'start', Key.enter)


def on_back(lc: LogitechController, kb: KeyboardController):
    binary_mapper(lc, kb, 'back', Key.backspace)


def on_a(lc: LogitechController, kb: KeyboardController):
    binary_mapper(lc, kb, 'A', Key.ctrl)


def on_x(lc: LogitechController, kb: KeyboardController):
    binary_mapper(lc, kb, 'X', Key.shift)


def on_b(lc: LogitechController, kb: KeyboardController):
    binary_mapper(lc, kb, 'B', Key.alt)


all_listeners = [f for f in globals().values() if callable(f) and str(f.__name__).startswith('on_')]
