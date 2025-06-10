import os
import unidecode

def transliterate_name(name):
    """Транслітерує строку з кирилиці на латиницю."""
    return unidecode.unidecode(name)

def transliterate_files_in_directory(directory_path):
    """Перейменовує файли в каталозі з кирилиці на латиницю."""
    for filename in os.listdir(directory_path):
        transliterated_name = transliterate_name(filename)
        original_path = os.path.join(directory_path, filename)
        new_path = os.path.join(directory_path, transliterated_name)
        if original_path != new_path:
            os.rename(original_path, new_path)
            print(f"Перейменовано: {filename} -> {transliterated_name}")

# Вказати шлях до вашого каталогу
directory_path = 'stl'
transliterate_files_in_directory(directory_path)