import os
import time
import re
from flask import current_app


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def allowed_file(filename):
    return (
        '.' in filename
        and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def save_fitting_image(file, name, old_path=None):
    """Сохраняет изображение фурнитуры, возвращает путь"""
    if not file or not file.filename or not allowed_file(file.filename):
        return old_path

    # Удаляем старое если есть
    if old_path:
        move_to_trash(old_path)

    # Создаём папку
    fittings_dir = os.path.join(
        current_app.static_folder,
        'images',
        'fittings'
    )

    os.makedirs(fittings_dir, exist_ok=True)

    # Получаем расширение из оригинального файла
    ext = file.filename.rsplit('.', 1)[1].lower()

    # Генерируем безопасное имя из переданного name
    # Заменяем пробелы на _, удаляем всё кроме букв, цифр, _ и -
    safe_name = re.sub(
        r'[^\w\-]', '',
        name.replace(' ', '_'),
        flags=re.UNICODE
    )
    if not safe_name:
        safe_name = 'image'

    # Формируем имя файла
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


def safe_folder_name(name):
    """Создаёт безопасное имя папки (сохраняет русские буквы)"""
    safe_name = re.sub(
        r'[^\w\-]', '',
        name.replace(' ', '_'),
        flags=re.UNICODE
    )
    if not safe_name:
        safe_name = 'folder'
    return safe_name


def create_kitchen_folders(kitchen_name):
    """Создает папки для типа кухни"""
    try:
        base_photo_path = os.path.join(
            current_app.static_folder,
            'images',
            'photo'
        )
        base_schemes_path = os.path.join(
            current_app.static_folder,
            'images',
            'schemes'
        )

        folder_name = safe_folder_name(kitchen_name)

        photo_folder = os.path.join(base_photo_path, folder_name)
        schemes_folder = os.path.join(base_schemes_path, folder_name)

        os.makedirs(photo_folder, exist_ok=True)
        os.makedirs(schemes_folder, exist_ok=True)

        return True, None
    except Exception as e:
        return False, str(e)


def rename_kitchen_folders(old_name, new_name):
    """Переименовывает папки типа кухни"""
    try:
        base_photo_path = os.path.join(
            current_app.static_folder,
            'images',
            'photo'
        )
        base_schemes_path = os.path.join(
            current_app.static_folder,
            'images',
            'schemes'
        )

        old_folder_name = safe_folder_name(old_name)
        new_folder_name = safe_folder_name(new_name)

        old_photo_folder = os.path.join(base_photo_path, old_folder_name)
        new_photo_folder = os.path.join(base_photo_path, new_folder_name)

        old_schemes_folder = os.path.join(base_schemes_path, old_folder_name)
        new_schemes_folder = os.path.join(base_schemes_path, new_folder_name)

        if os.path.exists(old_photo_folder):
            os.rename(old_photo_folder, new_photo_folder)

        if os.path.exists(old_schemes_folder):
            os.rename(old_schemes_folder, new_schemes_folder)

        return True, None
    except Exception as e:
        return False, str(e)
