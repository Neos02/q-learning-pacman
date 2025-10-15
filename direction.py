from pygame import Vector2


class Direction:
    LEFT = Vector2(-1, 0)
    UP = Vector2(0, -1)
    RIGHT = Vector2(1, 0)
    DOWN = Vector2(0, 1)
    NONE = Vector2(0, 0)
