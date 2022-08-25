from typing import Tuple

from pynput.keyboard import Key as Key

from controllers import Gamepad, KeyboardController, MouseController


def binary_mapper(gp: Gamepad, kb: KeyboardController, gp_key: Gamepad.Key, kb_key: Key):
    command_mapping = {
        0: kb.release,
        1: kb.press,
    }
    command_mapping[gp.state[gp_key]](kb_key)


def ternary_mapper(gp: Gamepad, kb: KeyboardController, gp_key: Gamepad.Key, kb_keys: Tuple[Key, Key]):
    command_mapping = {
        0: (kb.release, kb_keys),
        1: (kb.press, [kb_keys[0]]),
        -1: (kb.press, [kb_keys[1]]),
    }
    cmd, keys = command_mapping[gp.state[gp_key]]
    for k in keys:
        cmd(k)


def range_mapper(gp: Gamepad, m: MouseController, gp_key: Gamepad.Key, direction: str, converter, converter_kwargs={}):
    speed = converter(gp.state[gp_key], **converter_kwargs)
    if direction == 'x':
        m.mouse_speed_x = speed
    else:
        m.mouse_speed_y = speed

def linear_converter(s, a):
    signal = 1 if s > 0 else -1
    return signal * abs(s * a)
