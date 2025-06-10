import os
from stl import mesh
import numpy as np

directory_path = 'stl'  # Змініть на шлях до вашої папки з STL файлами

# Ініціалізація змінних для зберігання екстремальних значень
min_x, max_x = np.inf, -np.inf
min_y, max_y = np.inf, -np.inf
min_z, max_z = np.inf, -np.inf

# Проходження по всіх файлах у каталозі
for filename in os.listdir(directory_path):
    if filename.endswith('.stl'):
        # Завантаження STL файлу
        current_mesh = mesh.Mesh.from_file(os.path.join(directory_path, filename))
        
        # Оновлення екстремальних значень
        min_x = min(min_x, current_mesh.x.min())
        max_x = max(max_x, current_mesh.x.max())
        min_y = min(min_y, current_mesh.y.min())
        max_y = max(max_y, current_mesh.y.max())
        min_z = min(min_z, current_mesh.z.min())
        max_z = max(max_z, current_mesh.z.max())

# Обчислення розмірів паралелепіпеда
width = max_x - min_x
length = max_y - min_y
height = max_z - min_z

# Додавання додаткового простору для впевненості, що модель повністю покрита
padding = 10  # Можете змінити розмір додаткового простору за потребою

# Генерація коду для OpenSCAD
openscad_code = f'''
// Автоматично згенерований код OpenSCAD
translate([{min_x - padding / 2}, {min_y - padding / 2}, {min_z - padding / 2}]) {{
    cube([{width + padding}, {length + padding}, {height + padding}]);
}}
'''

print(openscad_code)
