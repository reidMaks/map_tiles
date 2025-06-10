from stl import mesh
import os
import numpy as np

# Встановлення шляху до каталогу і масштабу
directory_path = './stl/'
scale_factor = 0.4  # 40%
printer_size = (255, 210)  # Розміри столу принтера X, Y

def get_model_size(stl_path):
    model_mesh = mesh.Mesh.from_file(stl_path)
    size_x = np.max(model_mesh.x) - np.min(model_mesh.x)
    size_y = np.max(model_mesh.y) - np.min(model_mesh.y)
    size_z = np.max(model_mesh.z) - np.min(model_mesh.z)
    return (size_x, size_y, size_z)

def group_models(models, printer_size):
    groups = []
    current_group = []
    current_group_length = 0
    
    for model_name, dimensions in sorted(models.items(), key=lambda x: x[1][0], reverse=True):
        model_length = dimensions[0]
        if current_group_length + model_length <= printer_size[0]:
            current_group.append(model_name)
            current_group_length += model_length
        else:
            groups.append(current_group)
            current_group = [model_name]
            current_group_length = model_length
    
    if current_group:
        groups.append(current_group)
    
    return groups

# Завантаження та масштабування розмірів моделей
scaled_models = {}
for filename in os.listdir(directory_path):
    if filename.endswith('.stl'):
        model_path = os.path.join(directory_path, filename)
        original_size = get_model_size(model_path)
        scaled_size = tuple(dim * scale_factor for dim in original_size)
        scaled_models[filename] = scaled_size

# Групування моделей для друку
model_groups = group_models(scaled_models, printer_size)
for i, group in enumerate(model_groups, start=1):
    print(f"Група {i}: {', '.join(group)}")
