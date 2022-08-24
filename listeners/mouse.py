from controllers import LogitechController, MouseController
from mappers import range_mapper


def on_l_stick(lc: LogitechController, m: MouseController):
    range_mapper(lc, m, 'l_stick_x', 'x')
    range_mapper(lc, m, 'l_stick_y', 'y')


all_listeners = [f for f in globals().values() if callable(f) and str(f.__name__).startswith('on_')]
