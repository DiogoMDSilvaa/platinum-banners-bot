from dataclasses import dataclass, field
from typing import Set
from .game import Game


@dataclass
class Player:
    """Represents a player"""

    gamer_tag: str
    
    games: Set[Game] = field(default_factory = set)

   
