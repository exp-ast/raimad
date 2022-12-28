"""
Class for base component
"""

import numpy as np
from copy import deepcopy

from PyClewinSDC.LayerParams import LayerParams
from PyClewinSDC.Dotdict import Dotdict

# Possibilities:
# None can be used when parent and child have identical layers
# OR when both have only one layer
# str can be used to specify the layername of the parent
# when child has only one layer
# otherwise needs full dict
SubcomponentLayermapShorthand = None | str | dict
SubpolygonLayermapShorthand = None | str

Shadow = None


class Transformable(object):
    """
    Container for an affine matrix
    with methods to apply elementary transformations
    to that matrix.

    This is my first time working with affine matrices,
    so expect some obtuse code.
    """
    def __init__(self, affine_mat=None):
        if affine_mat is None:
            self.affine_mat = np.identity(3)
        else:
            self.affine_mat = affine_mat

    def fix_affine(self):
        self.affine_mat[2, 0] = 0
        self.affine_mat[2, 1] = 0
        self.affine_mat[2, 2] = 1

    def transform(self, transformable):
        """
        Apply another Transformable to this Transformable
        """
        self.affine_mat = np.matmul(
            transformable.affine_mat,
            self.affine_mat,
            )

    def translate(self, x, y):
        self.affine_mat = np.matmul(
            np.array([
                [1, 0, x],
                [0, 1, y],
                [0, 0, 1],
                ]),
            self.affine_mat,
            )
        self.fix_affine()

    def scale(self, x, y=None):
        if y is None:
            y = x
        self.affine_mat = np.matmul(
            np.array([
                [x, 0, 0],
                [0, y, 0],
                [1, 0, 1],
                ]),
            self.affine_mat,
            )
        self.fix_affine()

    def rotate(self, degrees):
        cosine = np.cos(np.radians(degrees))
        sine = np.sin(np.radians(degrees))
        self.affine_mat = np.matmul(
            np.array([
                [cosine, -sine, 0],
                [sine, cosine, 0],
                [1, 0, 1],
                ]),
            self.affine_mat,
            )
        self.fix_affine()


class Component(object):
    """
    Class for base component
    """
    optspecs = {}

    def __init__(self, *args, **kwargs):
        """
        args and kwargs are interpreted the same way as Dotdict,
        so can be used to set parameters during creation.
        """
        self.subcomponents = []
        self.subpolygons = []
        self.layers = []  # List of layer names
        self.set_opts(Dotdict(*args, **kwargs))

        self.layer_params = {}  # Maps layer names to parameters

    def update_opts(self, opts: dict):
        """
        Apply new options to component, keeping
        old ones in place.
        """
        if not set(opts.keys()).issubset(self.optspecs.keys()):
            raise Exception(
                "opts must be a subset of optspecs"
                )
        self.opts.update(opts)

    def set_opts(self, opts: dict):
        """
        Apply new options,
        overwriting old options.
        """
        if not set(opts.keys()).issubset(self.optspecs.keys()):
            raise Exception(
                "opts must be a subset of optspecs"
                )
        self.opts = Dotdict({
            name: optspec.default
            for name, optspec
            in self.optspecs.items()
            })
        self.opts.update(opts)

    def add_subcomponent(
            self,
            component,
            layermap_shorthand: SubcomponentLayermapShorthand = None,
            transform: Transformable | None = None,
            ):
        """
        Add new component as a subcomponent.
        """
        layermap = parse_subcomponent_layermap_shorthand(
            self.layers,
            component.layers,
            layermap_shorthand,
            )

        subcomponent = Subcomponent(
            component,
            layermap,
            )

        if transform is not None:
            subcomponent.transform(transform)

        self.subcomponents.append(subcomponent)

    def add_subpolygon(
            self,
            polygon,
            layermap: SubpolygonLayermapShorthand = None,
            transform: Transformable | None = None,
            ):
        """
        Layermap map subcomponent layers to component layers
        """
        layermap_full = parse_subpolygon_layermap_shorthand(
            self.layers,
            layermap
            )

        subpolygon = Subpolygon(
            polygon,
            layermap_full,
            )

        if transform is not None:
            subpolygon.transform(transform)

        self.subpolygons.append(subpolygon)

    def add_layer(self, name, fancy_name='', color1='', color2=''):
        self.layers.append(name)
        self.layer_params[name] = LayerParams(
            len(self.layers) - 1,
            name,
            fancy_name,
            color1,
            color2
            )

    def get_polygons(self, include_layers=None):
        """
        This should descend into subcomponents and subpolygons recursively,
        applying layermaps and transformations as it goes,
        to get a list of raw polygons in the end.

        returns dict mapping layers to polygons
        layers are same as self.layers

        include_layers is to specify which layers
        are needed, None means all.
        """
        if include_layers is None:
            include_layers = self.layers
        else:
            assert set(include_layers).issubset(self.layers)

        layers = {layer: [] for layer in include_layers}
        for subcomponent in self.subcomponents:
            for child_layer, polygons in subcomponent.get_polygons(include_layers).items():
                parent_layer = subcomponent.layermap[child_layer]
                if parent_layer is None:
                    continue
                layers[parent_layer].extend(polygons)

        for subpolygon in self.subpolygons:
            layers[subpolygon.layermap].extend(subpolygon.get_polygon(include_layers))

        return layers

    def make(self, opts=None):
        """
        This method should actually generate all subpolygons
        and subcomponents.

        This is an abstract base class,
        so here this method actually does nothing.

        opts allows to pass a custom options list

        Note that make() should work with all default parameters.
        This will actually be used for making the preview image.
        """

    @classmethod
    def parent(cls):
        """
        Return parent class.
        This is a shorthand for cls.__bases__[0]
        """
        return cls.__bases__[0]

    @classmethod
    def lint(cls):
        """
        Check whether this component class violtates any rules
        """
        if not cls.default_opts.keys() == cls.opt_descriptions.keys():
            print("Options and option descriptions don't match!")

        if len(cls.__bases__) > 1:
            print(
                "Multiple base classes detected. "
                "Please don't use multiple inheritance, "
                "it may seem like a smart choice now, "
                "but you will just hurt yourself in the end. "
                "A wiser approach is encapsulation."
                )
        # Big comment block here where I can jot down any other rules:
        #
        #
        #
        #
        #
        #


class Optspec(object):
    """
    Specification of an option:
    includes default value, description, shadow status
    """
    def __init__(self, default, desc='', shadow=False):
        self.default = default
        self.desc = desc
        self.shadow = bool(shadow)

    def get_shadow(self):
        """
        Get shadow version of this optspec
        """
        return Optspec(self.default, self.desc, True)


def make_opts(parent_class, **kwargs):
    """
    Helper function to generate options and option descriptions
    for a component class.
    You must pass in the parent class
    TODO add example
    """
    optspecs = Dotdict(parent_class.optspecs)
    for name, spec in kwargs.items():
        if spec is Shadow:
            optspecs[name] = parent_class.optspecs[name].get_shadow()
        else:
            optspecs[name] = Optspec(*spec)

    return optspecs


class Subcomponent(Transformable):
    def __init__(self, component, layermap):
        super().__init__()
        self.component = component
        self.layermap = layermap

    def get_polygons(self, include_layers):
        """
        This is the counterpart to component.get_polygons()
        that applies the correct transformations and everything.

        So basically it's a constant flip-flop between component.get_polygons()
        and subcomponent.get_polygons(), in a sort of tree,
        with the leaves being subpolygons
        """
        include_layers_child = [
            child_layer
            for child_layer, parent_layer in self.layermap.items()
            if parent_layer is not None
            ]

        child_layers = self.component.get_polygons(include_layers_child)
        transformed_layers = {}
        for layer_name, polygons in child_layers.items():
            transformed_layers[layer_name] = [
                poly.get_transformed(self.affine_mat)
                for poly in polygons
                ]

        return transformed_layers


class Subpolygon(Transformable):
    def __init__(self, polygon, layermap):
        super().__init__()
        self.polygon = polygon
        self.layermap = layermap

    def get_polygon(self, include_layers):
        """
        """
        if self.layermap in include_layers:
            return [self.polygon.get_transformed(self.affine_mat)]
        return []


def parse_subcomponent_layermap_shorthand(parent_layers, child_layers, layermap_shorthand: SubcomponentLayermapShorthand):
    if layermap_shorthand is None:
        if len(parent_layers) == len(child_layers):
            # Case One: parent and child the same number of layers
            layermap = dict(zip(child_layers, parent_layers))

        elif len(child_layers) == len(parent_layers) == 1:
            # Case Two: parent and child both have one layer
            # (not necessarily same name)
            layermap = {list(child_layers)[0]: list(parent_layers)[0]}
            # (the list() cast is in here just in case someone passes
            # something like a dict_keys object into this function
        else:
            raise Exception(
                "Could not parse None layermap shoarthand"
                )
    elif isinstance(layermap_shorthand, str):
        if len(child_layers) != 1:
            raise Exception(
                "You specified an str layermap shorthand, "
                "but the child component doesn't have "
                "just one layer."
                )

        if layermap_shorthand not in parent_layers:
            raise Exception(
                "You specified an str layermap shorthand, "
                "but that layer is not in the parent component."
                )

        layermap = {list(child_layers)[0]: layermap_shorthand}

    elif isinstance(layermap_shorthand, dict):
        if not set(layermap.keys()).issubset(child_layers):
            raise Exception(
                "Layermap keys are not a subset of child component layers"
                )

        if not set(layermap.values()).issubset(parent_layers):
            raise Exception(
                "Layermap values are not a subset of parent component layers"
                )

    else:
        raise Exception(
            "Layermap shorthand is incorrect type"
            )

    # Pad layermap
    for missing_layer in set(child_layers) - set(layermap):
        layermap[missing_layer] = None

    return layermap


def parse_subpolygon_layermap_shorthand(parent_layers, layermap_shorthand: SubpolygonLayermapShorthand):
    if layermap_shorthand is None:
        if len(parent_layers) == 1:
            return list(parent_layers)[0]
        else:
            raise Exception(
                "You specified a None layermap shorthand, "
                "but the parent component has more than one layer"
                )

    elif isinstance(layermap_shorthand, str):
        if layermap_shorthand in parent_layers:
            return layermap_shorthand
        else:
            raise Exception(
                "There is no such layer in parent component."
                )

    else:
        raise Exception(
            "Layermap shorthand is incorrect type"
            )


