from enum import auto, Enum


class GhostState(Enum):
    HOME = auto(),
    CHASE = auto(),
    EATEN = auto(),
    REVERSE = auto(),
    FRIGHTENED = auto()
