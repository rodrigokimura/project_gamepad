from controllers import LogitechController, KeyboardController, MouseController
from listeners.keyboard import all_listeners as keyboard_listeners
from listeners.mouse import all_listeners as mouse_listeners


class App:
    lc = LogitechController()
    kb = KeyboardController()
    m = MouseController()
    
    state = {}
    
    print_gamepad = True
    print_mouse = False
    m.print = print_mouse
    
    def run(self):
        while True:
            current_state = self.lc.read()
            if self.state != current_state:
                self.state = current_state
                if self.print_gamepad:
                    print(self.state)
                for listener in keyboard_listeners:
                    listener(self.lc, self.kb)
                for listener in mouse_listeners:
                    listener(self.lc, self.m)


app = App()


if __name__ == '__main__':
    app = App().run()
