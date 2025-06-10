filename = "default.stl"; // Значення за замовчуванням, якщо параметр не передано

z_height = 16;
z_offset = 14;
contour_shrink = -4; // Від'ємне значення для зменшення контуру

scale([0.4, 0.4, 0.4]) {
    linear_extrude(height = z_height - z_offset) {
        offset(r = contour_shrink) {
            projection(cut = true) {
                import(filename);
            }
        }
    }
}