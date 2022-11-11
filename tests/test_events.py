import pytest

from project_gamepad.events import InputController, OnStickMove


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
    fake_input_device.state["x"] = 1.0
    fake_input_device.state["y"] = 1.0
    assert OnStickMove(fake_input_device, ("x", "y")).is_set()
