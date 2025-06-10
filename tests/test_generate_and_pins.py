import os
import sys
import math
from shapely.geometry import (
    box,
    LineString,
    Polygon,
    MultiLineString,
    Point,
    GeometryCollection,
)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import map_generator.config as config
from map_generator.generate import calculate_scaling
from map_generator.pins import (
    safe_linemerge,
    should_skip_pair,
    is_valid_border,
    calculate_number_of_pins,
    calculate_normal_vector,
    calculate_pin_and_hole_positions,
    add_pin_and_hole,
    generate_pins_and_holes,
    find_pin_points_on_straight_segments,
)


class DummyMSP:
    def __init__(self):
        self.circles = []
        self.polylines = []

    def add_circle(self, center, radius):
        self.circles.append((center, radius))

    def add_lwpolyline(self, coords, close=False):
        self.polylines.append((coords, close))


def test_calculate_scaling():
    regions = {"a": box(0, 0, 10, 10), "b": box(0, 0, 20, 5)}
    scale_factor, min_x, min_y = calculate_scaling(regions)
    largest_extent = max(
        max(g.bounds[2] - g.bounds[0], g.bounds[3] - g.bounds[1])
        for g in regions.values()
    )
    assert scale_factor == config.TARGET_SIZE_MM / largest_extent
    assert min_x == 0
    assert min_y == 0


def test_safe_linemerge_merges_segments():
    geom = MultiLineString([[(0, 0), (1, 0)], [(1, 0), (2, 0)]])
    merged = safe_linemerge(geom)
    assert merged.coords[0] == (0.0, 0.0)
    assert merged.coords[-1] == (2.0, 0.0)


def test_safe_linemerge_complex():
    gc = GeometryCollection([
        LineString([(0, 0), (1, 0)]),
        LineString([(1, 0), (2, 0)]),
    ])
    result = safe_linemerge(gc)
    assert isinstance(result, LineString)


def test_safe_linemerge_point():
    pt = Point(0, 0)
    assert safe_linemerge(pt) == pt


def test_safe_linemerge_nested_multilinestring():
    nested = MultiLineString([
        [(0, 0), (1, 0)],
        [(1, 0), (2, 0)],
    ])

    class Outer:
        geom_type = "MultiLineString"

        def __init__(self, geoms):
            self.geoms = geoms

    outer = Outer([nested])
    merged = safe_linemerge(outer)
    assert list(merged.coords)[0] == (0.0, 0.0)


def test_should_skip_pair():
    processed = {tuple(sorted(["a", "b"]))}
    assert should_skip_pair("b", "a", processed)
    assert should_skip_pair("b", "b", set())
    assert not should_skip_pair("a", "c", set())


def test_is_valid_border():
    border = LineString([(0, 0), (1, 0)])
    assert not is_valid_border(border, scale_factor=0.1)
    assert is_valid_border(border, scale_factor=10)


def test_is_valid_border_empty():
    border = LineString()
    assert not is_valid_border(border, scale_factor=10)


def test_calculate_number_of_pins():
    length = 100
    scale = 1
    expected = max(1, int((length * scale - 2 * config.PIN_MARGIN_MM) // config.PIN_SPACING_MM))
    assert calculate_number_of_pins(length, scale) == expected


def test_calculate_normal_vector():
    border = LineString([(0, 0), (10, 0)])
    point = border.interpolate(5)
    polygon = Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
    nx, ny = calculate_normal_vector(border, point, polygon)
    assert math.isclose(nx, 0, abs_tol=1e-6)
    assert math.isclose(ny, -1, abs_tol=1e-6)


def test_calculate_normal_vector_zero_length():
    border = LineString([(0, 0), (0, 0)])
    point = border.interpolate(0)
    polygon = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
    nx, ny = calculate_normal_vector(border, point, polygon)
    assert (nx, ny) == (0, 0)


def test_calculate_pin_and_hole_positions():
    point = Point(0, 0)
    nx, ny = 1, 0
    pin, hole = calculate_pin_and_hole_positions(point, nx, ny, 2, 0, 0)
    shift_mm = (config.PIN_DIAMETER_MM / 2) + (config.OFFSET_MM / 2) - (
        config.PIN_DIAMETER_MM * 0.25
    )
    shift_hole_mm = shift_mm + config.OFFSET_MM
    expected_pin_x = (-nx * shift_mm)
    expected_hole_x = (-nx * shift_hole_mm)
    assert pin == (expected_pin_x, 0.0)
    assert hole == (expected_hole_x, 0.0)


def test_add_pin_and_hole():
    msp_pin = DummyMSP()
    msp_hole = DummyMSP()
    add_pin_and_hole(msp_pin, msp_hole, (1, 2), (3, 4))
    assert msp_pin.circles[0] == ((1, 2), config.PIN_DIAMETER_MM / 2)
    assert msp_hole.circles[0] == (
        (3, 4),
        (config.PIN_DIAMETER_MM + config.TOLERANCE_MM) / 2,
    )


def test_generate_contours():
    from map_generator.contours import generate_contours
    regions = {"a": Polygon([(0,0),(1,0),(1,1),(0,1)])}
    msp = DummyMSP()
    generate_contours(msp, regions, 10, 0, 0)
    assert msp.polylines and msp.polylines[0][1]


def test_find_pin_points_and_generate():
    regions = {
        "A": Polygon([(0,0),(1,0),(1,1),(0,1)]),
        "B": Polygon([(1,0),(2,0),(2,1),(1,1)])
    }
    msp_pin = DummyMSP()
    msp_hole = DummyMSP()
    generate_pins_and_holes(msp_pin, msp_hole, regions, 50, 0, 0)
    assert msp_pin.circles and msp_hole.circles
    # direct check of find_pin_points_on_straight_segments
    border = LineString([(0,0),(0,2),(0,4),(0,6),(0,8),(0,10)])
    points = find_pin_points_on_straight_segments(border, 5, window_size=3, min_segment_length_mm=0)
    assert points


def test_find_pin_points_multipart_and_invalid():
    border = MultiLineString([
        [(0, 0), (1, 0)],
        [(2, 0), (3, 0)]
    ])
    pts = find_pin_points_on_straight_segments(border, 50)
    assert isinstance(pts, list)
    assert find_pin_points_on_straight_segments(Point(0, 0), 1) == []


def test_generate_pins_skips_invalid_border():
    regions = {
        "A": Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
        "B": Polygon([(2, 0), (3, 0), (3, 1), (2, 1)])
    }
    msp_pin = DummyMSP()
    msp_hole = DummyMSP()
    generate_pins_and_holes(msp_pin, msp_hole, regions, 50, 0, 0)
    assert not msp_pin.circles and not msp_hole.circles


def test_find_pin_points_deviation_skip():
    line = LineString([(0, 0), (1, 0), (2, 5), (3, 0), (4, 0)])
    pts = find_pin_points_on_straight_segments(line, 1, window_size=5, deviation_ratio=0.01, min_segment_length_mm=0)
    assert pts == []


def test_find_pin_points_short_segment_skip():
    line = LineString([(0, 0), (5, 0), (10, 0), (15, 0), (20, 0)])
    pts = find_pin_points_on_straight_segments(line, 1, window_size=5, min_segment_length_mm=1000)
    assert pts == []


def test_find_pin_points_skips_non_line(monkeypatch):
    border = LineString([(0, 0), (10, 0)])

    class DummyLine:
        geom_type = "Point"

    dummy = type("Dummy", (), {"geom_type": "MultiLineString", "geoms": [DummyLine(), border]})
    monkeypatch.setattr('map_generator.pins.safe_linemerge', lambda *a, **k: dummy)
    points = find_pin_points_on_straight_segments(border, 1, window_size=3, min_segment_length_mm=0)
    assert points
