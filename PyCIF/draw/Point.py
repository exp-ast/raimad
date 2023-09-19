"""
Point -- storage for x, y coordinate pair
"""
from typing import Self
from copy import copy

import numpy as np

import PyCIF as pc

class Point(object, metaclass=pc.SlotsFromAnnotationsMeta):
    _x: float
    _y: float

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    def __init__(self, x: float = 0, y: float = 0, arg: float | None = None, mag: float | None = None):
        """
        Create a point from (x, y)
        with short syntax: pc.Point(10, 20)
        """
        if arg is not None:
            self._x = np.cos(arg) * mag
            self._y = np.sin(arg) * mag
        else:
            self._x = x
            self._y = y

    # TODO better overloading framework. Should support:
    # pc.Point()  # create an origin
    # pc.Point(10, 10)  # x, y
    # pc.Point(x=10, y=10)  # x, y
    # pc.Point(arg=pc.degrees(45), mag=10)  # polar
    # pc.Point(arg=pc.degrees(45))  # polar, mag is 1

    def __repr__(self):
        return f"Point({self.x:.3f}, {self.y:.3f})"

    def __iter__(self):
        """
        Iterator method allows unpacking
        a CoordPair into [x, y]
        """
        return iter((self.x, self.y))

    def __add__(self, other):
        """
        Allow adding CoordPairs together
        """
        new = self.copy()
        new._x += other[0]
        new._y += other[1]
        return new

    def __sub__(self, other):
        """
        Allow subtractin CoordPairs
        """
        new = self.copy()
        new._x -= other[0]
        new._y -= other[1]
        return new

    def __rsub__(self, other):
        """
        Allow subtractin CoordPairs
        """
        new = self.copy()
        new._x = other[0] - self._x
        new._y = other[1] - self._y
        return new

    def __pos__(self):
        return self

    def __neg__(self):
        # TODO neg creates a copy, but pos doesnt. What do?
        # Should makes points immovable?
        return self * -1

    def __truediv__(self, other: Self | int | float):
        if isinstance(other, type(self)):
            return Point(
                self.x / other[0],
                self.y / other[1]
                )

        elif isinstance(other, float | int):
            return Point(
                self.x / other,
                self.y / other
                )

        raise Exception("idk wtf to do with this")


    def __getitem__(self, index):
        if index == 0:
            return self.x

        if index == 1:
            return self.y

        raise Exception("Points consist of only two coordinates")

    #def __setitem__(self, index, value):
    #    if index == 0:
    #        self.x = value

    #    elif index == 1:
    #        self.y == value

    #    else:
    #        raise Exception("Points consist of only two coordinates")

    #def move(self, x, y):
    #    self.x += x
    #    self.y += y
    #    return self

    def __array__(self):
        return np.array((self.x, self.y))

    #@classmethod
    #def Polar(cls, arg: float, mag: float = 1):
    #    return cls(
    #        np.cos(angle) * magnitude,
    #        np.sin(angle) * magnitude
    #        )

    def __eq__(self, other):
        return self.distance_to(other) < 0.001  # TODO delta

    @property
    def arg(self):
        return np.arctan2(self.y, self.x)

    @property
    def mag(self):
        return np.linalg.norm(self)

    def distance_to(self, other: Self):
        """
        Also see pc.Point.distance_from and pc.distance_between
        """
        return np.linalg.norm(other - self)

    def distance_from(self, other: Self):
        """
        Also see pc.Point.distance_to and pc.distance_between
        """
        return np.linalg.norm(self - other)

    #def apply_transform(self, transform: pc.Transform):
    #    # TODO forms of this are copy-pasted in multiple places.
    #    self.x, self.y, _ = transform.get_matrix().dot(
    #            np.array([self.x, self.y, 1]))
    #    return self

    def copy(self):
        # TODO???
        return copy(self)

    def canonical(self):
        return self.copy()

