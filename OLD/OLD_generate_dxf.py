import json
import os
import sys
import ezdxf
import math
from shapely.geometry import shape, mapping
from shapely.affinity import translate
from pyproj import Transformer

# === Settings ===
PIN_DIAMETER_MM = 5.0
PIN_SPACING_MM = 40.0
PIN_MARGIN_MM = 3.0
TOLERANCE_MM = 0.3
TARGET_SIZE_MM = 250
OFFSET_MM = 0.2

EXCLUDE_REGIONS = ['Kyiv', "Sevastopol'"]

# === Transformer WGS84 -> UTM Zone 36N (for Ukraine)
transformer = Transformer.from_crs("EPSG:4326", "EPSG:32636", always_xy=True)

def project_geometry(geom):
    return shape({
        'type': geom.geom_type,
        'coordinates': _project_coords(geom)
    })

def _project_coords(geom):
    if geom.geom_type == 'Polygon':
        return [list(map(lambda coord: transformer.transform(*coord), ring)) for ring in geom.exterior.coords],
    elif geom.geom_type == 'MultiPolygon':
        return [
            [list(map(lambda coord: transformer.transform(*coord), poly.exterior.coords))]
            for poly in geom.geoms
        ]

def load_regions(source_file):
    with open(source_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    VALID_TYPES = ["Oblast'", "AutonomousRepublic"]
    features = [x for x in data['features'] 
                if x['properties'].get('TYPE_1') in VALID_TYPES 
                and x['properties'].get('NAME_1') not in EXCLUDE_REGIONS]

    regions = {}
    for feature in features:
        name = feature['properties']['NAME_1'].replace(" ", "_")
        geom = shape(feature['geometry'])
        projected_geom = project_geometry(geom)
        regions[name] = projected_geom
    return regions

def calculate_scaling(regions):
    largest_extent = max([
        max(g.bounds[2] - g.bounds[0], g.bounds[3] - g.bounds[1])
        for g in regions.values()
    ])
    scale_factor = TARGET_SIZE_MM / largest_extent
    min_x = min([g.bounds[0] for g in regions.values()])
    min_y = min([g.bounds[1] for g in regions.values()])
    return scale_factor, min_x, min_y


def generate_dxf_files(regions, buffered_regions, scale_factor, min_x, min_y):
    os.makedirs("tmp", exist_ok=True)

    doc_map = ezdxf.new()
    doc_map.units = ezdxf.units.MM
    msp_map = doc_map.modelspace()

    doc_pins = ezdxf.new()
    doc_pins.units = ezdxf.units.MM
    msp_pins = doc_pins.modelspace()

    doc_holes = ezdxf.new()
    doc_holes.units = ezdxf.units.MM
    msp_holes = doc_holes.modelspace()

    doc_full = ezdxf.new()
    doc_full.units = ezdxf.units.MM
    msp_full = doc_full.modelspace()

    processed_pairs = set()
    pair_index = 0
    MIN_STITCH_LENGTH_MM = PIN_DIAMETER_MM

    for region_a, geom_a in buffered_regions.items():
        polygons = geom_a.geoms if geom_a.geom_type == 'MultiPolygon' else [geom_a]
        for poly in polygons:
            coords = [((x - min_x) * scale_factor, (y - min_y) * scale_factor) for x, y in poly.exterior.coords]
            msp_map.add_lwpolyline(coords, close=True)
            msp_full.add_lwpolyline(coords, close=True)

    for region_a, geom_a in regions.items():
        for region_b, geom_b in regions.items():
            if region_a >= region_b:
                continue

            key = tuple(sorted([region_a, region_b]))
            if key in processed_pairs:
                continue

            border = geom_a.boundary.intersection(geom_b.boundary)
            if border.is_empty or border.length == 0:
                continue

            if (border.length * scale_factor) < MIN_STITCH_LENGTH_MM:
                continue

            num_pins = max(1, int((border.length * scale_factor - 2 * PIN_MARGIN_MM) // PIN_SPACING_MM))

            if pair_index % 2 == 0:
                pin_owner = region_a
                hole_owner = region_b
            else:
                pin_owner = region_b
                hole_owner = region_a
            pair_index += 1

            for i in range(num_pins):
                point = border.interpolate((i + 1) * (border.length / (num_pins + 1)))

                delta = 0.01 * border.length
                p1 = border.interpolate(max(0, point.distance(border) - delta))
                p2 = border.interpolate(min(border.length, point.distance(border) + delta))

                dx = p2.x - p1.x
                dy = p2.y - p1.y

                length = math.hypot(dx, dy)
                if length == 0:
                    continue

                nx = -dy / length
                ny = dx / length

                test_point = translate(point, nx * 0.0005, ny * 0.0005)
                if geom_a.contains(test_point):
                    nx = -nx
                    ny = -ny

                shift_mm = (PIN_DIAMETER_MM / 2) + (OFFSET_MM / 2) - (PIN_DIAMETER_MM * 0.25)
                shift_hole_mm = shift_mm + OFFSET_MM

                shift_deg = shift_mm / scale_factor
                shift_hole_deg = shift_hole_mm / scale_factor

                x_pin = point.x - nx * shift_deg
                y_pin = point.y - ny * shift_deg

                x_hole = point.x - nx * shift_hole_deg
                y_hole = point.y - ny * shift_hole_deg

                x_pin_mm = (x_pin - min_x) * scale_factor
                y_pin_mm = (y_pin - min_y) * scale_factor

                x_hole_mm = (x_hole - min_x) * scale_factor
                y_hole_mm = (y_hole - min_y) * scale_factor

                msp_pins.add_circle((x_pin_mm, y_pin_mm), PIN_DIAMETER_MM / 2)
                msp_holes.add_circle((x_hole_mm, y_hole_mm), (PIN_DIAMETER_MM + TOLERANCE_MM) / 2)

                msp_full.add_circle((x_pin_mm, y_pin_mm), PIN_DIAMETER_MM / 2)
                msp_full.add_circle((x_hole_mm, y_hole_mm), (PIN_DIAMETER_MM + TOLERANCE_MM) / 2)

            processed_pairs.add(key)

    doc_map.saveas("tmp/ukraine_map.dxf")
    doc_pins.saveas("tmp/ukraine_pins.dxf")
    doc_holes.saveas("tmp/ukraine_holes.dxf")
    doc_full.saveas("tmp/ukraine_full.dxf")


def main():
    if len(sys.argv) != 2:
        print("❌ Використання: python generate_dxf_with_pins.py <шлях_до_geojson>")
        sys.exit(1)

    source_file = sys.argv[1]
    regions = load_regions(source_file)
    scale_factor, min_x, min_y = calculate_scaling(regions)

    offset_in_deg = OFFSET_MM / scale_factor
    buffered_regions = {name: geom.buffer(-offset_in_deg) for name, geom in regions.items()}

    generate_dxf_files(regions, buffered_regions, scale_factor, min_x, min_y)

    print("\n✅ Збережено файли у папці tmp:")
    print(" - Контури:    ukraine_map.dxf")
    print(" - Піни:       ukraine_pins.dxf")
    print(" - Отвори:     ukraine_holes.dxf")
    print(" - Все разом:  ukraine_full.dxf")


if __name__ == "__main__":
    main()
