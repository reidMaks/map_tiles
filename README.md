# Map Tiles Generator

This project converts simplified GeoJSON data of Ukrainian regions into DXF files. The
`map_generator` package contains the main logic to generate contours, alignment pins
and city labels. The `OLD` folder keeps previous attempts at STL generation and can
serve as historical reference.

## Quick start

1. Build the Docker image:

```bash
docker build -t topojson-tool .
```

2. Run the helper script `run_topojson.sh`. It will create a simplified GeoJSON file and
   generate the DXF maps in one go:

```bash
./run_topojson.sh
```

DXF files will be placed in `tmp/` by default:

- `ukraine_map.dxf` – only region contours
- `ukraine_pins.dxf` – pins
- `ukraine_holes.dxf` – holes
- `ukraine_full.dxf` – all features together

## Previewing DXF files

A simple web viewer is available at `viewer/index.html`. Open this file in your
browser (for example using the VS Code Live Preview extension) and choose one of
the generated DXF files from the `tmp/` directory to inspect it.

If you prefer running the generator without Docker, install the Python
requirements and call the script manually:

```bash
pip install -r requirements.txt
python3 -m map_generator.generate path/to/simplified.geojson
```

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

