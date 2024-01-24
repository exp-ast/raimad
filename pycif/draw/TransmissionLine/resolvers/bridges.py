from dataclasses import dataclass
from random import Random
from typing import Iterable

import numpy as np

import pycif as pc
from pycif.draw import TransmissionLine as tl

# Get a random number generator with a fixed seed,
# so that bridge spacing is deterministic.
# This is better than using `random.seed`, since it won't
# set the seed for anyone else who might be using the `random`
# module.
bridge_rng = Random(42)
# TODO this needs to exist for every transmission line, not globally,
# so that e.g. the order you make transmission lines in doesnt
# change bridge positions.

@dataclass
class BridgeSpec:
    start: pc.Point
    angle: float
    length: float

def construct_bridges(path, spacing, scramble, bridge_length, do_bridges=True, striped=False):
    newpath = []
    specs = []

    default_do_bridges = do_bridges
    default_spacing = spacing
    default_scramble = scramble
    default_bridge_length = bridge_length

    for conn, after in pc.iter.duplets(path):

        spacing = (
            after.bridge_spacing if after.bridge_spacing is not None else
            (spacing if striped else default_spacing)
            )
        scramble = (
            after.bridge_scramble if after.bridge_scramble is not None else
            (scramble if striped else default_scramble)
            )
        bridge_length = (
            after.bridge_length if after.bridge_length is not None else
            (bridge_length if striped else default_bridge_length)
            )
        do_bridges = (
            after.do_bridges if after.do_bridges is not None else
            (do_bridges if striped else default_do_bridges)
            )

        # TODO clean up this spaghett

        if not isinstance(after, tl.StraightTo):
            continue

        if not do_bridges:
            newpath.append(after)
            continue

        leg_distance = pc.distance_between(conn.to, after.to)
        leg_angle = pc.angle_between(conn.to, after.to)
        # TODO minimum leg length check)

        distances = np.arange(
            spacing,
            leg_distance - spacing,
            spacing
            )

        newpath.append(conn)
        newpath.append(
            tl.JumpTo(
                conn.to + pc.Point(arg=leg_angle, mag=bridge_length),
                )
            )
        specs.append(BridgeSpec(
            start=conn.to,
            angle=leg_angle,
            length=bridge_length
            ))

        for distance in distances:
            distance += bridge_rng.uniform(-1, 1) * scramble

            enter_point = (
                conn.to + pc.Point(
                    arg=leg_angle,
                    mag=(distance - bridge_length / 2)
                    )
                )

            newpath.append(
                tl.StraightTo(
                        enter_point
                    )
                )
            newpath.append(
                tl.JumpTo(
                    conn.to + pc.Point(
                        arg=leg_angle,
                        mag=(distance + bridge_length / 2)
                        )
                    )
                )
            specs.append(BridgeSpec(
                start=enter_point,
                angle=leg_angle,
                length=bridge_length
                ))

        enter_point = (
            after.to + pc.Point(
                arg=leg_angle,
                mag=-bridge_length
                )
            )
        newpath.append(
            tl.StraightTo(
                    enter_point
                )
            )
        newpath.append(
            tl.JumpTo(
                after.to
                )
            )
        specs.append(tl.BridgeSpec(
            start=enter_point,
            angle=leg_angle,
            length=bridge_length,
            ))

    # TODO split up and refactor this CHONKER of a function
    return newpath, specs

def make_bridge_compo(spec: BridgeSpec, Compo: pc.typing.CompoClass):
    return (
        Compo(options=dict(length=spec.length))
        .marks.tl_enter.to(spec.start)
        .marks.tl_enter.rotate(spec.angle)
        )

def make_bridge_compos(
        specs: Iterable[BridgeSpec],
        Compo: pc.typing.CompoClass,
        ):
    return [
        make_bridge_compo(spec, Compo)
        for spec in specs
        ]

