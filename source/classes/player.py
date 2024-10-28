from dataclasses import dataclass
from typing import Set
from .game import Game


@dataclass
class Player:
    """Represents a player"""

    gamer_tag: str
    
    games: Set[Game] = set()

   
