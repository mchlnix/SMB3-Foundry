class Rect:
    def __init__(self, x=0, y=0, width=0, height=0):
        self.x = x
        self.y = y

        self.width = width
        self.height = height

        if self.width < 0:
            self.width *= -1
            self.x -= self.width

        if self.height < 0:
            self.height *= -1
            self.y -= self.height

    def point_in(self, x: int, y: int, include_borders=True) -> bool:
        """

        :param x: X coordinate of the point to check.
        :param y: Y coordinate of the point to check.
        :param include_borders: Whether a point on the right or bottom border of the rect is considered inside.
        """
        if not include_borders:
            return self.x <= x < self.x + self.width and self.y <= y < self.y + self.height
        else:
            return self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height

    def intersects(self, other: "Rect"):
        if other.x + other.width <= self.x:
            return False

        if other.y + other.height <= self.y:
            return False

        if other.x >= self.x + self.width:
            return False

        if other.y >= self.y + self.height:
            return False

        return True

    def contains(self, other: "Rect"):
        return self.point_in(*other.top_left()) and self.point_in(*other.bottom_right())

    def size(self):
        return self.width, self.height

    def top(self):
        return self.y

    def bottom(self):
        return self.y + self.height

    def left(self):
        return self.x

    def right(self):
        return self.x + self.width

    def top_left(self):
        return Point(self.x, self.y)

    def top_right(self):
        return Point(self.x + self.width, self.y)

    def bottom_left(self):
        return Point(self.x, self.y + self.height)

    def bottom_right(self):
        return Point(self.x + self.width, self.y + self.height)

    def __iter__(self):
        return iter((self.x, self.y, self.width, self.height))

    def __mul__(self, other):
        if not isinstance(other, (int, float)):
            raise TypeError("Rect can only be multiplied by an integer or float")

        return Rect(self.x * other, self.y * other, self.width * other, self.height * other)


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def copy(self):
        return Point(self.x, self.y)

    def __add__(self, other):
        if not isinstance(other, Point):
            raise TypeError("Point can only be added to another Point")

        return Point(self.x + other.x, self.y + other.y)

    def __iter__(self):
        return iter((self.x, self.y))
