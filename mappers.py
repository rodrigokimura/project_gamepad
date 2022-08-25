from typing import Tuple

from pynput.keyboard import Key

from controllers import LogitechController, KeyboardController, MouseController


def binary_mapper(lc: LogitechController, kb: KeyboardController, lc_attr, kb_key: Key):
    command_mapping = {
        0: kb.release,
        1: kb.press,
    }
    command_mapping[getattr(lc, lc_attr)](kb_key)


def ternary_mapper(lc: LogitechController, kb: KeyboardController, lc_attr, kb_keys: Tuple[Key, Key]):
    command_mapping = {
        0: (kb.release, kb_keys),
        1: (kb.press, [kb_keys[0]]),
        -1: (kb.press, [kb_keys[1]]),
    }
    cmd, keys = command_mapping[getattr(lc, lc_attr)]
    for k in keys:
        cmd(k)


def range_mapper(lc: LogitechController, m: MouseController, lc_attr, direction: str, converter, converter_kwargs={}):
    lc_ev_state = getattr(lc, lc_attr)
    speed = converter(lc_ev_state, **converter_kwargs)
    if direction == 'x':
        m.mouse_speed_x = speed
    else:
        m.mouse_speed_y = speed

def linear_converter(s, a):
    signal = 1 if s > 0 else -1
    return signal * abs(s * a)
