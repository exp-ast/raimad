"""
Class for base component
"""

import numpy as np

from PyClewinSDC.LayerParams import LayerParams

# Possibilities:
# None can be used when parent and child have identical layers
# OR when both have only one layer
# str can be used to specify the layername of the parent
# when child has only one layer
# otherwise needs full dict
SubcomponentLayermapShorthand = None | str | dict
SubpolygonLayermapShorthand = None | str


class Component(object):
    """
    Class for base component
    """
    def __init__(self):
        """
        """
        self.subcomponents = []
        self.subpolygons = []
        self.layers = []

        self.layer_params = {}

    def add_layer(self, name, color1='', color2=''):
        self.layers.append(name)
        self.layer_params[name] = LayerParams(
            len(self.layers) - 1,
            name,
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
            for layer, polygons in subcomponent.get_polygons(include_layers).items():
                layers[layer].extend(polygons)

        for subpolygon in self.subpolygons:
            layers[subpolygon.layermap].extend(subpolygon.get_polygon(include_layers))

        return layers

    def add_shape(self, shape, layer):
        self.layers[layer].append(shape)

    def add_shapes(self, shapes, layer):
        self.layers[layer].extend(shapes)

    def add_subcomponent(self, component, layermap_shorthand: SubcomponentLayermapShorthand = None):
        """
        Layermap map subcomponent layers to component layers
        """
        layermap = parse_subcomponent_layermap_shorthand(
            self.layers,
            component.layers,
            layermap_shorthand,
            )

        self.subcomponents.append(Subcomponent(component, layermap))

    def add_subpolygon(self, component, layermap_shorthand: SubpolygonLayermapShorthand = None):
        """
        Layermap map subcomponent layers to component layers
        """
        layermap = parse_subpolygon_layermap_shorthand(
            self.layers,
            layermap_shorthand
            )

        self.subpolygons.append(Subpolygon(component, layermap))


class Subcomponent(object):
    def __init__(self, component, layermap):
        self.component = component
        self.layermap = layermap
        self.affine_mat = np.identity(3)

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


class Subpolygon(object):
    def __init__(self, polygon, layermap):
        self.polygon = polygon
        self.layermap = layermap
        self.affine_mat = np.identity(3)

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
    for missing_layer in set(child_layers) - set(parent_layers):
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



