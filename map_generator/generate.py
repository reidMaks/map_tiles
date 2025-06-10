# generate.py

import os
import ezdxf
import sys
from map_generator.regions import load_regions
from map_generator.contours import generate_contours
from map_generator.pins import generate_pins_and_holes
from map_generator.cities import load_cities, add_cities_to_dxf
import map_generator.config as config

def calculate_scaling(regions):
    largest_extent = max([
        max(g.bounds[2] - g.bounds[0], g.bounds[3] - g.bounds[1])
        for g in regions.values()
    ])
    scale_factor = config.TARGET_SIZE_MM / largest_extent
    min_x = min([g.bounds[0] for g in regions.values()])
    min_y = min([g.bounds[1] for g in regions.values()])
    return scale_factor, min_x, min_y

def main():

    if len(sys.argv) != 2:
        print("❌ Використання: python generate.py <шлях_до_geojson>")
        sys.exit(1)

    source_file = sys.argv[1]
    regions = load_regions(source_file)
    scale_factor, min_x, min_y = calculate_scaling(regions)
    cities = load_cities()

    offset_in_deg = config.OFFSET_MM / scale_factor
    buffered_regions = {name: geom.buffer(-offset_in_deg) for name, geom in regions.items()}

    os.makedirs(config.OUTPUT_DIR, exist_ok=True)

    # DXF документи
    doc_map = ezdxf.new()
    doc_pins = ezdxf.new()
    doc_holes = ezdxf.new()
    doc_full = ezdxf.new()

    for doc in [doc_map, doc_pins, doc_holes, doc_full]:
        doc.units = ezdxf.units.MM

    msp_map = doc_map.modelspace()
    msp_pins = doc_pins.modelspace()
    msp_holes = doc_holes.modelspace()
    msp_full = doc_full.modelspace()

    # Генерація
    generate_contours(msp_map, buffered_regions, scale_factor, min_x, min_y)
    generate_contours(msp_full, buffered_regions, scale_factor, min_x, min_y)

    generate_pins_and_holes(msp_pins, msp_holes, regions, scale_factor, min_x, min_y)
    generate_pins_and_holes(msp_full, msp_full, regions, scale_factor, min_x, min_y)

    add_cities_to_dxf(msp_full, cities, scale_factor, min_x, min_y)

    # Збереження
    doc_map.saveas(f"{config.OUTPUT_DIR}/ukraine_map.dxf")
    doc_pins.saveas(f"{config.OUTPUT_DIR}/ukraine_pins.dxf")
    doc_holes.saveas(f"{config.OUTPUT_DIR}/ukraine_holes.dxf")
    doc_full.saveas(f"{config.OUTPUT_DIR}/ukraine_full.dxf")

    print("\n✅ Всі файли збережено у tmp/")

if __name__ == "__main__":  # pragma: no cover
    main()  # pragma: no cover
