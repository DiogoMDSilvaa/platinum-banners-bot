from dataclasses import dataclass
from datetime import datetime


@dataclass
class Platinum:
    """Represents a platinum trophy"""

    difficulty: int

    playthroughs: int

    hours: int

    date_earned: datetime
