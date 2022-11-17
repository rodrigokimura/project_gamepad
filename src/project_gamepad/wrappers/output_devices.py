try:
    from pynput.keyboard import Controller as KeyboardController
    from pynput.keyboard import Key as KeyboardKey
    from pynput.mouse import Button as MouseKey
    from pynput.mouse import Controller as MouseController
except ImportError:
    # HACK: workaround to run tests in the CI environment
    class KeyboardController:
        pass

    class KeyboardKey:
        pass

    class MouseKey:
        pass

    class MouseController:
        pass
