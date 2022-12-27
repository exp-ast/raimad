"""
Scalable Vector Graphics Exporter
"""

from PyClewinSDC.Component import Component


def get_bounding_box(polygons):
    max_x = float('-inf')
    max_y = float('-inf')
    min_x = float('inf')
    min_y = float('inf')

    for layer, polys in polygons.items():
        for poly in polys:
            for point in poly.xyarray:
                if point[0] > max_x:
                    max_x = point[0]
                elif point[0] < min_x:
                    min_x = point[0]

                if point[1] > max_y:
                    max_y = point[1]
                elif point[1] < min_y:
                    min_y = point[1]

    return min_x, min_y, max_x, max_y


def SVGExporter(stream, component: Component):
    polygons = component.get_polygons()

    min_x, min_y, max_x, max_y = get_bounding_box(polygons)

    stream.write(
        '<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{max_x - min_x}" '
        f'height="{max_y - min_y}">\n'
        )

    for layer_name, polys in polygons.items():
        for poly in polys:
            stream.write('\t<polygon points="')
            for point in poly.xyarray:
                stream.write(f"{point[0] - min_x},{point[1] - min_y} ")
            stream.write('" />\n')

    stream.write('</svg>\n')

