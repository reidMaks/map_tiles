# Map Tiles Generator

This project converts simplified GeoJSON data of Ukrainian regions into DXF files. The
`map_generator` package contains the main logic to generate contours, alignment pins
and city labels. The `OLD` folder keeps previous attempts at STL generation and can
serve as historical reference.

## Quick start

1. Install Python dependencies:

```bash
pip install -r requirements.txt
```

2. Prepare a simplified GeoJSON file. A helper script `run_topojson.sh` can run inside a
docker container to build one from `source_data/gadm41_UKR_1.json` and output a smoothed
file. After running it you will have a file like `source_data/simplified_gadm41_UKR_1_P-0.7.json`.

3. Generate DXF maps:

```bash
python3 -m map_generator.generate path/to/simplified.geojson
```

DXF files will be placed in `tmp/` by default:

- `ukraine_map.dxf` – only region contours
- `ukraine_pins.dxf` – pins
- `ukraine_holes.dxf` – holes
- `ukraine_full.dxf` – all features together

## Project structure

- `map_generator/` – core code
- `source_data/` – input datasets
- `tests/` – automated tests
- `OLD/` – earlier experiments for generating STL files

## Possible improvements

- Switch to `argparse` in `generate.py` to expose command line options for the
  output directory or disabling particular features.
- Cache loaded city data in `cities.py` to avoid re-reading the JSON file on each
  invocation.
- Add type annotations for easier maintenance.

