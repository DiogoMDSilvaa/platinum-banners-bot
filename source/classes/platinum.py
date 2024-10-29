from dataclasses import dataclass
from datetime import datetime


@dataclass
class Platinum:
    """Represents a platinum trophy"""

    difficulty: int | None

    playthroughs: int | None

    hours: int | None

    date_earned: datetime
