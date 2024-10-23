from dataclasses import dataclass
from enum import Enum, auto


from .platinum import Platinum


class Console(Enum):
    """Represents the possible consoles"""

    PS3 = auto()
    PS4 = auto()
    PS5 = auto()


@dataclass
class Game:
    """Represents a general playstation game"""

    name: str

    console: Console

    banner: str

    platinum: Platinum = None
