import pytest

from project_gamepad.events import InputController, OnKeyPress, OnStickMove, OnStickStop


class FakeInputController(InputController):
    def __init__(self):
        self.state = {
            "x": 0.0,
            "y": 0.0,
        }

    def _monitor_controller(self):
        pass


@pytest.fixture
def fake_input_device():
    return FakeInputController()


def test_on_stick_move_should_not_set(fake_input_device: InputController):
    assert OnStickMove(fake_input_device, ("x", "y")).is_set() is False


def test_on_stick_move_should_set(fake_input_device: InputController):
    fake_input_device.state["x"] = 0.1
    fake_input_device.state["y"] = 0.1
    assert OnStickMove(fake_input_device, ("x", "y")).is_set()


def test_on_stick_stop_should_not_set(fake_input_device: InputController):
    assert OnStickStop(fake_input_device, ("x", "y")).is_set()


def test_on_stick_stop_should_set(fake_input_device: InputController):
    fake_input_device.state["x"] = 0.1
    assert OnStickStop(fake_input_device, ("x", "y")).is_set() is False


def test_on_key_press_should_not_set(fake_input_device: InputController):
    assert OnKeyPress(fake_input_device, ("x", "y")).is_set() is False
    fake_input_device.state["y"] = 1
    assert OnKeyPress(fake_input_device, ("x", "y")).is_set() is False


def test_on_key_press_should_set(fake_input_device: InputController):
    fake_input_device.state["x"] = 1
    fake_input_device.state["y"] = 1
    assert OnKeyPress(fake_input_device, ("x", "y")).is_set() is True
