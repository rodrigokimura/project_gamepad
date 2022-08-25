from controllers import LogitechController, MouseController
from mappers import range_mapper, linear_converter


def on_r_stick(lc: LogitechController, m: MouseController):
    range_mapper(lc, m, 'r_stick_x', 'x', linear_converter, {'a': 20})
    range_mapper(lc, m, 'r_stick_y', 'y', linear_converter, {'a': 20})


all_listeners = [f for f in globals().values() if callable(f) and str(f.__name__).startswith('on_')]
