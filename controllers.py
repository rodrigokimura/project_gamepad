import threading
from time import sleep

from inputs import get_gamepad
from pynput.keyboard import Controller as _KeyboardController
from pynput.mouse import Controller as _MouseController


class KeyboardController(_KeyboardController):
    pass


class MouseController(_MouseController):

    def __init__(self) -> None:
        super().__init__()
        self.print = True
        self.mouse_speed_x = 0
        self.mouse_speed_y = 0
        self._stopped = True
        self._delay = 0.01
        self._monitor_thread = threading.Thread(target=self._monitor_controller, args=())
        self._monitor_thread.daemon = True
        self._monitor_thread.start()
        
    def stop(self) -> None:
        self._stopped = True

    def start(self) -> None:
        self._stopped = False

    def move(self):
        # if self._stopped:
        #     return
        print(self.mouse_speed_x, self.mouse_speed_y)
        super().move(
            self.mouse_speed_x,
            self.mouse_speed_y,
        )

    def _monitor_controller(self) -> None:
        while True:
            if self.print:
                print(self.mouse_speed_x, self.mouse_speed_y)
            if self._delay:
                sleep(self._delay)
            self.move()


class LogitechController:
    MAX_TRIG_VAL = 2**8
    MAX_JOY_VAL = 2**15
    MAPPING = {
        ('Key', 'BTN_SOUTH'): 'A',
        ('Key', 'BTN_EAST'): 'B',
        ('Key', 'BTN_NORTH'): 'X',
        ('Key', 'BTN_WEST'): 'Y',
        ('Absolute', 'ABS_HAT0X'): 'H',
        ('Absolute', 'ABS_HAT0Y'): 'V',
        ('Key', 'BTN_TL'): 'LB',
        ('Key', 'BTN_TR'): 'RB',
        ('Absolute', 'ABS_Z'): 'LT',
        ('Absolute', 'ABS_RZ'): 'RT',
        ('Key', 'BTN_START'): 'start',
        ('Key', 'BTN_SELECT'): 'back',
        ('Key', 'BTN_MODE'): 'center',
        ('Absolute', 'ABS_X'): 'l_stick_x',
        ('Absolute', 'ABS_Y'): 'l_stick_y',
        ('Absolute', 'ABS_RX'): 'r_stick_x',
        ('Absolute', 'ABS_RY'): 'r_stick_y',
        ('Key', 'BTN_THUMBL'): 'l_thumb',
        ('Key', 'BTN_THUMBR'): 'r_thumb',
    }
    TO_NORMALIZE = {
        ('Absolute', 'ABS_X'): MAX_JOY_VAL,
        ('Absolute', 'ABS_Y'): MAX_JOY_VAL,
        ('Absolute', 'ABS_RX'): MAX_JOY_VAL,
        ('Absolute', 'ABS_RY'): MAX_JOY_VAL,
        ('Absolute', 'ABS_Z'): MAX_TRIG_VAL,
        ('Absolute', 'ABS_RZ'): MAX_TRIG_VAL,
    }

    def __init__(self):

        self.A = 0
        self.B = 0
        self.X = 0
        self.Y = 0
        
        self.H = 0
        self.V = 0
        
        self.LB = 0
        self.RB = 0
        self.LT = 0
        self.RT = 0
        
        self.start = 0
        self.back = 0
        self.center = 0
        
        self.l_stick_x = 0
        self.l_stick_y = 0
        self.r_stick_x = 0
        self.r_stick_y = 0
        self.l_thumb = 0
        self.r_thumb = 0

        self._monitor_thread = threading.Thread(target=self._monitor_controller, args=(False, 2))
        self._monitor_thread.daemon = True
        self._monitor_thread.start()


    def read(self):
        d_pad = [self.H, self.V]
        buttons = [
            self.A,
            self.B,
            self.X,
            self.Y,
        ]
        special = [self.back, self.start, self.center]
        sticks = [
            (self.l_stick_x, self.l_stick_y, self.l_thumb), 
            (self.r_stick_x, self.r_stick_y, self.r_thumb),
        ]
        upper = [self.LB, self.RB, self.LT, self.RT]
        d = locals()
        del d['self']
        return d


    def _monitor_controller(self, print_ev=False, stick_precision=1) -> None:
        
        while True:
            events = get_gamepad()
            for ev in events:
                t = (ev.ev_type, ev.code)
                if print_ev:
                    print(t)
                if t in self.MAPPING:
                    state = ev.state
                    if t in self.TO_NORMALIZE:
                        state = round(ev.state / self.TO_NORMALIZE[(ev.ev_type, ev.code)], stick_precision)
                    setattr(
                        self,
                        self.MAPPING[(ev.ev_type, ev.code)],
                        state
                    )
