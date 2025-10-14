import math


class Vector:

    def __init__(self, x: int = 0, y: int = 0):
        self.x: int = x
        self.y: int = y

    def magnitude(self) -> float:
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def normalized(self) -> 'Vector':
        return self * (1 / self.magnitude())

    def __add__(self, other) -> 'Vector':
        if isinstance(other, Vector):
            return Vector(self.x + other.x, self.y + other.y)
        elif isinstance(other, (int, float)):
            return self + Vector(other, other)

        return NotImplemented

    __radd__ = __add__

    def __sub__(self, other) -> 'Vector':
        if isinstance(other, Vector):
            return Vector(self.x - other.x, self.y - other.y)
        elif isinstance(other, (int, float)):
            return self - Vector(other, other)

        return NotImplemented

    def __rsub__(self, other) -> 'Vector':
        if isinstance(other, Vector):
            return Vector(other.x - self.x, other.y - self.y)
        elif isinstance(other, (int, float)):
            return Vector(other, other) - self

        return NotImplemented

    def __mul__(self, other) -> 'Vector':
        if isinstance(other, (int, float)):
            return Vector(self.x * other, self.y * other)

        return NotImplemented

    __rmul__ = __mul__

    def __neg__(self) -> 'Vector':
        return Vector(-self.x, -self.y)

    def __abs__(self) -> 'Vector':
        return Vector(abs(self.x), abs(self.y))

    def __repr__(self) -> str:
        return f"Vector({self.x}, {self.y})"

    def __str__(self) -> str:
        return f'({self.x}, {self.y})'
