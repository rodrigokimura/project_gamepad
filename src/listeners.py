from typing import Collection

from commands import Command
from events import Event


class Listener:
    event: Event
    commands: Collection[Command]

    def __init__(self, event, commands) -> None:
        self.event = event
        self.commands = commands

    def listen(self) -> None:
        if self.event.is_set():
            for cmd in self.commands:
                cmd.run(self.event.context)
