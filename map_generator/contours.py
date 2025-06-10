# contours.py

import map_generator.config as config

def generate_contours(msp_map, regions, scale_factor, min_x, min_y):
    """Генерація контурів областей у DXF."""
    for name, geom in regions.items():
        polygons = geom.geoms if geom.geom_type == 'MultiPolygon' else [geom]
        for poly in polygons:
            coords = [((x - min_x) * scale_factor, (y - min_y) * scale_factor) for x, y in poly.exterior.coords]
            msp_map.add_lwpolyline(coords, close=True)
    print(f"✅ Генерація контурів завершена")
