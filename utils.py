import os
import time
from werkzeug.utils import secure_filename
from flask import current_app

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_fitting_image(file, name, old_path=None):
    """Сохраняет изображение фурнитуры, возвращает путь"""
    if not file or not file.filename or not allowed_file(file.filename):
        return old_path
    
    # Удаляем старое если есть
    if old_path:
        move_to_trash(old_path)
    
    # Создаём папку
    fittings_dir = os.path.join(current_app.static_folder, 'images', 'fittings')
    os.makedirs(fittings_dir, exist_ok=True)
    
    # Получаем расширение
    ext = file.filename.rsplit('.', 1)[1].lower()
    
    # Генерируем безопасное имя: заменяем пробелы на _, удаляем всё кроме букв, цифр, _ и -
    import re
    safe_name = re.sub(r'[^\w\-]', '', name.replace(' ', '_'))
    if not safe_name:
        safe_name = 'image'
    
    filename = f"{safe_name}.{ext}"
    filepath = os.path.join(fittings_dir, filename)
    
    # Если файл существует, добавляем номер
    if os.path.exists(filepath):
        counter = 1
        while os.path.exists(filepath):
            filename = f"{safe_name}_{counter}.{ext}"
            filepath = os.path.join(fittings_dir, filename)
            counter += 1
    
    file.save(filepath)
    return f'static/images/fittings/{filename}'


def move_to_trash(filepath):
    """Перемещает файл в папку trash"""
    if not filepath:
        return
    
    # Преобразуем путь к абсолютному
    full_path = os.path.join(current_app.root_path, filepath)
    
    if not os.path.exists(full_path):
        return
    
    trash_dir = os.path.join(current_app.static_folder, 'images', 'trash')
    os.makedirs(trash_dir, exist_ok=True)
    
    filename = os.path.basename(full_path)
    trash_path = os.path.join(trash_dir, filename)
    
    # Если файл уже есть в trash, добавляем timestamp
    if os.path.exists(trash_path):
        name, ext = os.path.splitext(filename)
        trash_path = os.path.join(trash_dir, f"{name}_{int(time.time())}{ext}")
    
    os.rename(full_path, trash_path)

def delete_fitting_image(filepath):
    """Удаляет изображение (в корзину)"""
    if filepath:
        move_to_trash(filepath)