"""
Arc polygon
"""

from typing import ClassVar
from enum import Enum

import numpy as np

import PyCIF as pc

class Arc(pc.Polygon):
    radius_inner: ClassVar[float]
    radius_outter: ClassVar[float]
    angle: ClassVar[float]

    @pc.kwoverload
    def __init__(
            self,
            angle_start: float,
            angle_end: float,
            orientation: pc.Orientation = pc.Orientation.Counterclockwise,
            *,
            radius_inner: float,
            radius_outter: float,
            ):
        super().__init__()

        self.radius_inner = radius_inner
        self.radius_outter = radius_outter
        self.angle_start = angle_start
        self.angle_end = angle_end
        self.orientation = orientation
        self.radial_center = (self.radius_inner + self.radius_outter) / 2

        self._set_marks()

    @__init__.register
    def _(
            self,
            angle_start: float,
            angle_end: float,
            orientation: pc.Orientation = pc.Orientation.Counterclockwise,
            *,
            radius_inner: float,
            radial_width: float,
            ):
        super().__init__()

        self.radius_inner = radius_inner
        self.radius_outter = radius_inner + radial_width
        self.angle_start = angle_start
        self.angle_end = angle_end
        self.orientation = orientation
        self.radial_center = (self.radius_inner + self.radius_outter) / 2

        self._set_marks()

    @__init__.register
    def _(
            self,
            angle_start: float,
            angle_end: float,
            orientation: pc.Orientation = pc.Orientation.Counterclockwise,
            *,
            radius_outter: float,
            radial_width: float,
            ):
        super().__init__()

        self.radius_inner = radius_outter - radial_width
        self.radius_outter = radius_outter
        self.angle_start = angle_start
        self.angle_end = angle_end
        self.orientation = orientation
        self.radial_center = (self.radius_inner + self.radius_outter) / 2

        self._set_marks()

    @__init__.register
    def _(
            self,
            angle_start: float,
            angle_end: float,
            orientation: pc.Orientation = pc.Orientation.Counterclockwise,
            *,
            radial_center: float,
            radial_width: float,
            ):
        super().__init__()

        self.radius_inner = radial_center - radial_width / 2
        self.radius_outter = radial_center + radial_width / 2
        self.angle_start = angle_start
        self.angle_end = angle_end
        self.orientation = orientation
        self.radial_center = radial_center

        self._set_marks()


    def _set_marks(self):
        self._add_mark(
            'center',
            pc.point(0, 0),
            'Center of the arc',
            )

        self._add_mark(
            'start_mid',
            pc.point_polar(self.angle_start) * self.radial_center,
            'Midway between the two radii, at the start of the arc'
            )

        self._add_mark(
            'end_mid',
            pc.point_polar(self.angle_end) * self.radial_center,
            'Midway between the two radii, at the end of the arc'
            )

    def _get_xyarray(self):

        if self.angle_start == self.angle_end:
            return np.array([])

        angspace = pc.angspace(
            self.angle_start,
            self.angle_end,
            orientation=self.orientation,
            )

        return np.array([
            pc.point_polar(angle) * radius
            for radius, angles in [
                [self.radius_inner, angspace],
                [self.radius_outter, reversed(angspace)],
                ]
            for angle in angles
            ])

