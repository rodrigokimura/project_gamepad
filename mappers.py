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


def range_mapper(lc: LogitechController, m: MouseController, lc_attr, direction: str):
    lc_ev_state = getattr(lc, lc_attr)
    # if abs(lc_ev_state) <= .1:
    #     m.stop()
    #     return
    # else:
    #     m.start()
    
    speed = lc_ev_state * 50
    if direction == 'x':
        m.mouse_speed_x = speed
    else:
        m.mouse_speed_y = speed
