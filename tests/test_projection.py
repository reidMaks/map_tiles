import os
import sys
import pytest
from shapely.geometry import Polygon, Point, MultiPolygon
from pyproj import Transformer

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import map_generator.config as config
from map_generator.projection import project_geometry


def test_project_geometry_polygon():
    poly = Polygon([(30, 50), (31, 50), (31, 51), (30, 51), (30, 50)])
    projected = project_geometry(poly)
    transformer = Transformer.from_crs(config.WGS84_EPSG, config.UTM_EPSG, always_xy=True)
    expected = [transformer.transform(x, y) for x, y in poly.exterior.coords]
    assert list(projected.exterior.coords) == expected


def test_project_geometry_invalid_type():
    with pytest.raises(ValueError):
        project_geometry(Point(0, 0))


def test_project_geometry_multipolygon():
    mp = MultiPolygon([
        Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
        Polygon([(2, 2), (3, 2), (3, 3), (2, 3)])
    ])
    projected = project_geometry(mp)
    transformer = Transformer.from_crs(config.WGS84_EPSG, config.UTM_EPSG, always_xy=True)
    for poly, out_poly in zip(mp.geoms, projected.geoms):
        expected = [transformer.transform(x, y) for x, y in poly.exterior.coords]
        assert list(out_poly.exterior.coords) == expected
