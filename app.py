from controllers import Gamepad, KeyboardController, MouseController
from listeners.keyboard import all_listeners as keyboard_listeners
from listeners.mouse import all_listeners as mouse_listeners
from commands import PressKey


class App:
    gp = Gamepad()
    kb = KeyboardController()
    m = MouseController()
    
    state = {}
    
    print_gamepad = True
    print_mouse = False
    m.print = print_mouse
    
    def run(self):
        while True:
            current_state = self.gp.read()
            if self.state != current_state:
                self.state = current_state
                if self.print_gamepad:
                    print(self.state)
                for listener in keyboard_listeners:
                    listener(self.gp, self.kb)
                for listener in mouse_listeners:
                    listener(self.gp, self.m)


app = App()


if __name__ == '__main__':
    app = App().run()
