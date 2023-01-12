import numpy as np

from PyClewinSDC.Component import Component, make_opts, Shadow, make_layers
from PyClewinSDC.Polygon import Polygon
from PyClewinSDC.PolygonGroup import PolygonGroup
from PyClewinSDC.OptCategory import Geometric


class LeakyAntennaExample(Component):
    """
    Leaky antenna example
    Long description Long description Long description
    Long description Long description Long description
    Long description Long description Long description
    Long description Long description Long description
    Long description Long description Long description
    Long description Long description Long description.
    """
    optspecs = make_opts(
        Component,
        width=(100, "Membrane width", Geometric),
        overlap=(2, "??? in um", Geometric),
        thickness=(100, "Membrane thickness", Geometric),
        )

    layerspecs = make_layers(
        Component,
        koh=('', ),
        sin=('', ),
        gnd=('Ground', ),
        eb=('Main Layer', ),
        mesh=('Mesh Layer', ),
        diel=('Dielectric', ),
        )

    def make(self, opts=None):
        if opts is None:
            opts = self.opts

        self.make_butterfly(opts)

    def make_butterfly(self, opts):

        theta = np.radians(15)  # ??
        ladd0 = opts.overlap / np.tan((np.pi / 2 + theta) / 2)
        ladd1 = opts.overlap / np.tan((np.pi / 2 - theta) / 2)
        htotal = 351
        wtotal = 500
        wslot = 10  # ?? thickness of cpw?
        hslot = htotal * (wslot / 2) / (wtotal / 2)
        ltaper = (wtotal - wslot) / 2
        lcpwadd = 20

        #go(self.hSlot/2., self.wSlot/2.*updown)

        diagonal = Polygon(
            [
                [
                    0,
                    0,
                ],
                [
                    0,
                    2 * opts.overlap + ladd0,
                ],
                [
                    ltaper,
                    (htotal - hslot) / 2 + 2 * opts.overlap + ladd0,
                ],
                [
                    ltaper,
                    (htotal - hslot) / 2,
                ],
            ])

        barlength = htotal + 2 * opts.overlap + 2 * ladd1
        vertical = Polygon.rect_wh(
            0,
            -barlength / 2,
            2 * opts.overlap,
            barlength,
            )

        wing_right = PolygonGroup(
            diagonal,
            diagonal.copy().hflip().movey(-wslot / 2),
            vertical.copy().movex(ltaper),
            )

        wing_left = wing_right.copy().vflip()

        self.add_subpolygons(wing_right, 'eb')
        self.add_subpolygons(wing_left, 'eb')


        #go(-self.hSlot/2., self.wSlot/2.*updown)

