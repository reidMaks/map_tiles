import math
from shapely.affinity import translate
import map_generator.config as config

def generate_pins_and_holes(msp_pins, msp_holes, regions, scale_factor, min_x, min_y):
    processed_pairs = set()

    for region_a, geom_a in regions.items():
        for region_b, geom_b in regions.items():
            if should_skip_pair(region_a, region_b, processed_pairs):
                continue

            border = geom_a.boundary.intersection(geom_b.boundary)
            if not is_valid_border(border, scale_factor):
                continue

            # num_pins = calculate_number_of_pins(border.length, scale_factor)

            pin_points = find_pin_points_on_straight_segments(
                            border,
                            scale_factor=scale_factor,
                            window_size=5,                 # Наприклад, 6 точок для аналізу
                            deviation_ratio=0.3,           # 30% від діаметра піну
                            min_segment_length_mm=30,      # Мінімум 30 мм рівної ділянки
                            pin_spacing_mm=config.PIN_SPACING_MM
                        )

            for point in pin_points:
                nx, ny = calculate_normal_vector(border, point, geom_a)

                pin_center_mm, hole_center_mm = calculate_pin_and_hole_positions(
                    point, nx, ny, scale_factor, min_x, min_y
                )

                add_pin_and_hole(msp_pins, msp_holes, pin_center_mm, hole_center_mm)

            processed_pairs.add(tuple(sorted([region_a, region_b])))

    print(f"✅ Генерація пінів та отворів завершена")


from shapely.geometry import LineString, Point, MultiLineString
from shapely.ops import linemerge

def safe_linemerge(geometry):
    # Вибираємо лише LineString і MultiLineString з >= 2 точками
    lines = []

    if geometry.geom_type in ('LineString', 'MultiLineString'):
        geoms = geometry.geoms if geometry.geom_type == 'MultiLineString' else [geometry]
        for geom in geoms:
            if geom.geom_type == 'LineString' and len(geom.coords) >= 2:
                lines.append(geom)
            elif geom.geom_type == 'MultiLineString':
                for subgeom in geom.geoms:
                    if len(subgeom.coords) >= 2:
                        lines.append(subgeom)
    elif geometry.geom_type == 'GeometryCollection':
        for geom in geometry.geoms:
            if geom.geom_type in ('LineString', 'MultiLineString'):
                lines.append(geom)

    if not lines:
        return geometry  # Повертаємо як є, якщо нічого зливати

    return linemerge(MultiLineString(lines))

def find_pin_points_on_straight_segments(border, scale_factor, window_size=5, deviation_ratio=0.25, min_segment_length_mm=30, pin_spacing_mm=40):
    """
    Знаходить точки для пінів на рівних ділянках кордону.
    Переводить девіації в міліметри перед порівнянням.
    """
    # 1️⃣ Об'єднуємо лінії
    merged_border = safe_linemerge(border)

    max_deviation_mm = min((config.PIN_DIAMETER_MM * deviation_ratio), 30)
    print(f"🔹 Аналіз локальних ділянок (max_deviation = {max_deviation_mm:.2f} мм)")

    pin_points = []

    lines = []
    if merged_border.geom_type == 'MultiLineString':
        lines = list(merged_border.geoms)
    elif merged_border.geom_type == 'LineString':
        lines = [merged_border]
    else:
        print(f"⚠️ Непідтримуваний тип геометрії: {merged_border.geom_type}")
        return []

    for line in lines:
        if line.geom_type != 'LineString':
            continue

        coords = list(line.coords)

        if len(coords) < window_size:
            # Якщо коротка лінія — ставимо пін по центру, якщо дозволяє довжина
            segment_length_mm = line.length * scale_factor
            if segment_length_mm >= min_segment_length_mm:
                num_pins = max(1, int((segment_length_mm - 2 * config.PIN_MARGIN_MM) // pin_spacing_mm))
                for j in range(num_pins):
                    dist = (j + 1) * (line.length / (num_pins + 1))
                    pin_points.append(line.interpolate(dist))
            continue

        for i in range(len(coords) - window_size + 1):
            window = coords[i:i + window_size]
            base_line = LineString([window[0], window[-1]])

            deviations = [base_line.distance(Point(p)) for p in window[1:-1]]
            deviations_mm = [d * scale_factor for d in deviations]  # Переводимо в міліметри

            print(f"🔹 Вікно {i}: {deviations_mm}")

            if max(deviations_mm) > max_deviation_mm:
                continue

            segment = LineString(window)
            segment_length_mm = segment.length * scale_factor

            if segment_length_mm < min_segment_length_mm:
                continue

            num_pins = max(1, int((segment_length_mm - 2 * config.PIN_MARGIN_MM) // pin_spacing_mm))
            for j in range(num_pins):
                dist_on_segment = (j + 1) * (segment.length / (num_pins + 1))
                point_on_segment = segment.interpolate(dist_on_segment)

                distance_on_line = line.project(point_on_segment)
                point_on_border = line.interpolate(distance_on_line)

                pin_points.append(point_on_border)

    print(f"🎯 Всього пінів знайдено: {len(pin_points)}\n")
    return pin_points


def should_skip_pair(region_a, region_b, processed_pairs):
    if region_a >= region_b:
        return True
    key = tuple(sorted([region_a, region_b]))
    return key in processed_pairs


def is_valid_border(border, scale_factor):
    if border.is_empty or border.length == 0:
        return False
    if (border.length * scale_factor) < config.PIN_DIAMETER_MM:
        return False
    return True


def calculate_number_of_pins(border_length, scale_factor):
    return max(1, int((border_length * scale_factor - 2 * config.PIN_MARGIN_MM) // config.PIN_SPACING_MM))


def calculate_normal_vector(border, point, geom_a):
    delta = 0.01 * border.length
    p1 = border.interpolate(max(0, point.distance(border) - delta))
    p2 = border.interpolate(min(border.length, point.distance(border) + delta))

    dx = p2.x - p1.x
    dy = p2.y - p1.y

    length = math.hypot(dx, dy)
    if length == 0:
        return 0, 0

    nx = -dy / length
    ny = dx / length

    test_point = translate(point, nx * 0.0005, ny * 0.0005)
    if geom_a.contains(test_point):
        nx = -nx
        ny = -ny

    return nx, ny


def calculate_pin_and_hole_positions(point, nx, ny, scale_factor, min_x, min_y):
    shift_mm = (config.PIN_DIAMETER_MM / 2) + (config.OFFSET_MM / 2) - (config.PIN_DIAMETER_MM * 0.25)
    shift_hole_mm = shift_mm + config.OFFSET_MM

    shift_deg = shift_mm / scale_factor
    shift_hole_deg = shift_hole_mm / scale_factor

    x_pin = point.x - nx * shift_deg
    y_pin = point.y - ny * shift_deg

    x_hole = point.x - nx * shift_hole_deg
    y_hole = point.y - ny * shift_hole_deg

    pin_center_mm = ((x_pin - min_x) * scale_factor, (y_pin - min_y) * scale_factor)
    hole_center_mm = ((x_hole - min_x) * scale_factor, (y_hole - min_y) * scale_factor)

    return pin_center_mm, hole_center_mm


def add_pin_and_hole(msp_pins, msp_holes, pin_center_mm, hole_center_mm):
    msp_pins.add_circle(pin_center_mm, config.PIN_DIAMETER_MM / 2)
    msp_holes.add_circle(hole_center_mm, (config.PIN_DIAMETER_MM + config.TOLERANCE_MM) / 2)
