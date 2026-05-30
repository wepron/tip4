from flask import (render_template,
                   request, redirect,
                   url_for, flash, current_app)

from models import Color, Fitting, KitchenType, KitchenBase, Module
from extensions import db
# from werkzeug.utils import secure_filename
from pathlib import Path
import os


# Убираем secure_filename из импорта, так как она уже есть в utils
from utils import (
    save_fitting_image,
    delete_fitting_image,
    create_kitchen_folders,
    rename_kitchen_folders
)


# /static/images/photos_module/{kitchen_type_id}/


def save_module_photo(file, module_name, kitchen_type_name, old_path=None):
    if not file or file.filename == '':
        return old_path

    if old_path:
        old_full_path = Path(current_app.root_path) / 'static' / old_path
        if old_full_path.exists():
            old_full_path.unlink()

    safe_type = kitchen_type_name.replace(' ', '_')
    safe_name = module_name.replace(' ', '_')

    ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'jpg'
    filename = f"{safe_type}_{safe_name}_photo.{ext}"

    # Используем Path - он сам ставит правильные слеши
    filepath = Path('images') / 'photos_module' / safe_type / filename
    filepath = str(filepath).replace('\\', '/')  # конвертируем для URL

    full_path = Path(current_app.root_path) / 'static' / filepath

    full_path.parent.mkdir(parents=True, exist_ok=True)

    with open(full_path, 'wb') as f:
        file.save(f)

    return filepath


def save_module_scheme(file, module_name, kitchen_type_name, old_path=None):
    if not file or file.filename == '':
        return old_path

    # Удаляем старый файл, если есть
    if old_path:
        old_full_path = Path(current_app.root_path) / 'static' / old_path
        if old_full_path.exists():
            old_full_path.unlink()

    # Очищаем имена
    safe_type = kitchen_type_name.replace(' ', '_')
    safe_name = module_name.replace(' ', '_')

    # Получаем расширение
    ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'jpg'
    filename = f"{safe_type}_{safe_name}_scheme.{ext}"

    # Формируем путь (для БД и URL)
    filepath = Path('images') / 'schemes_module' / safe_type / filename
    filepath = str(filepath).replace('\\', '/')

    # Полный путь для сохранения
    full_path = Path(current_app.root_path) / 'static' / filepath

    # Создаем папки и сохраняем
    full_path.parent.mkdir(parents=True, exist_ok=True)
    file.save(str(full_path))

    return filepath


def register_routes(app):

    @app.route('/')
    def index():
        return render_template('index.html', show_header=False)

    @app.route('/deals')
    def deals():
        return render_template('deals.html', show_header=True)

    @app.route('/stickers')
    def stickers():
        return render_template('stickers.html', show_header=True)

    @app.route('/configurator')
    def configurator():
        return render_template('configurator.html', show_header=True)

    @app.route('/colors')   # Просмотр всех цветов
    def colors():
        colors = Color.query.all()  # получаем все цвета из БД
        return render_template('colors.html', colors=colors, show_header=True)

    # Создание нового цвета
    @app.route('/colors/create', methods=['GET', 'POST'])
    def color_create():
        if request.method == 'POST':
            name = request.form['name']
            short_name = request.form['short_name']

            # Проверка на дубликаты
            existing = Color.query.filter_by(short_name=short_name).first()
            if existing:
                flash('Цвет с таким коротким именем уже существует!', 'error')
                return redirect(url_for('color_create'))

            color = Color(name=name, short_name=short_name)
            db.session.add(color)
            db.session.commit()

            flash('Цвет успешно создан!', 'success')
            return redirect(url_for('colors'))

        return render_template(
            'color_form.html',
            title='Создать цвет',
            color=None
        )

    # Редактирование цвета
    @app.route('/colors/edit/<int:id>', methods=['GET', 'POST'])
    def color_edit(id):
        color = Color.query.get_or_404(id)

        if request.method == 'POST':
            color.name = request.form['name']
            color.short_name = request.form['short_name']
            db.session.commit()

            flash('Цвет успешно обновлён!', 'success')
            return redirect(url_for('colors'))

        return render_template(
            'color_form.html',
            title='Редактировать цвет',
            color=color
        )

    # Удаление цвета
    @app.route('/colors/delete/<int:id>', methods=['POST'])
    def color_delete(id):
        color = Color.query.get_or_404(id)
        db.session.delete(color)
        db.session.commit()  # ← коммит после удаления

        flash('Цвет успешно удалён!', 'success')
        return redirect(url_for('colors'))

    ###########################################################################
    @app.route('/configurator/modules')
    def modules():
        modules = Module.query.all()
        return render_template('modules.html',
                               modules=modules,
                               show_header=True)

    # Создание модуля
    @app.route('/modules/create', methods=['GET', 'POST'])
    def module_create():
        if request.method == 'POST':
            name = request.form['name']
            short_name = request.form['short_name']
            kitchen_base_id = request.form['kitchen_base_id']
            kitchen_type_id = int(request.form['kitchen_type_id'])
            boxes = request.form.get('boxes', type=int)

            # Получаем название типа кухни (текст, не ID)
            kitchen_type = KitchenType.query.get(kitchen_type_id)
            kitchen_type_name = kitchen_type.name if kitchen_type else "unknown"

            module = Module(
                name=name,
                short_name=short_name,
                kitchen_base_id=kitchen_base_id,
                kitchen_type_id=kitchen_type_id,
                boxes=boxes
            )

            db.session.add(module)
            db.session.commit()

            # Сохраняем фото
            if 'photo_path' in request.files and request.files['photo_path'].filename:
                module.photo_path = save_module_photo(
                    request.files['photo_path'],
                    name,
                    kitchen_type_name,
                    None
                )

            # Сохраняем схему
            if 'scheme_path' in request.files and request.files['scheme_path'].filename:
                module.scheme_path = save_module_scheme(
                    request.files['scheme_path'],
                    name,
                    kitchen_type_name,
                    None
                )

            db.session.commit()

            flash('Модуль успешно создан!', 'success')
            return redirect(url_for('modules'))

        kitchen_bases = KitchenBase.query.all()
        kitchen_types = KitchenType.query.all()

        return render_template(
            'module_form.html',
            title='Создать модуль',
            module=None,
            kitchen_bases=kitchen_bases,
            kitchen_types=kitchen_types
        )

    # Редактирование модуля
    @app.route('/modules/edit/<int:id>', methods=['GET', 'POST'])
    def module_edit(id):
        module = Module.query.get_or_404(id)

        if request.method == 'POST':
            old_kitchen_type_name = module.kitchen_type.name if module.kitchen_type else "unknown"
            new_kitchen_type_id = int(request.form['kitchen_type_id'])

            new_kitchen_type = KitchenType.query.get(new_kitchen_type_id)
            new_kitchen_type_name = new_kitchen_type.name if new_kitchen_type else "unknown"

            module.name = request.form['name']
            module.short_name = request.form['short_name']
            module.kitchen_base_id = request.form['kitchen_base_id']
            module.kitchen_type_id = new_kitchen_type_id
            module.boxes = request.form.get('boxes', type=int)

            # Обновляем фото
            if 'photo_path' in request.files and request.files['photo_path'].filename:
                module.photo_path = save_module_photo(
                    request.files['photo_path'],
                    module.name,
                    new_kitchen_type_name,
                    module.photo_path
                )
            elif old_kitchen_type_name != new_kitchen_type_name and module.photo_path:
                # Перемещаем фото при смене типа кухни
                old_full = os.path.join(current_app.root_path,
                                        'static',
                                        module.photo_path)
                new_path = module.photo_path.replace(old_kitchen_type_name,
                                                     new_kitchen_type_name)
                new_full = os.path.join(current_app.root_path,
                                        'static',
                                        new_path)
                if os.path.exists(old_full):
                    os.makedirs(os.path.dirname(new_full), exist_ok=True)
                    os.rename(old_full, new_full)
                    module.photo_path = new_path

            # Обновляем схему
            if 'scheme_path' in request.files and request.files['scheme_path'].filename:
                module.scheme_path = save_module_scheme(
                    request.files['scheme_path'],
                    module.name,
                    new_kitchen_type_name,
                    module.scheme_path
                )
            elif old_kitchen_type_name != new_kitchen_type_name and module.scheme_path:
                old_full = os.path.join(current_app.root_path,
                                        'static',
                                        module.scheme_path)
                new_path = module.scheme_path.replace(old_kitchen_type_name,
                                                      new_kitchen_type_name)
                new_full = os.path.join(current_app.root_path,
                                        'static',
                                        new_path)
                if os.path.exists(old_full):
                    os.makedirs(os.path.dirname(new_full), exist_ok=True)
                    os.rename(old_full, new_full)
                    module.scheme_path = new_path

            db.session.commit()

            flash('Модуль успешно обновлён!', 'success')
            return redirect(url_for('modules'))

        kitchen_bases = KitchenBase.query.all()
        kitchen_types = KitchenType.query.all()

        return render_template(
            'module_form.html',
            title='Редактировать модуль',
            module=module,
            kitchen_bases=kitchen_bases,
            kitchen_types=kitchen_types
        )

    # Удаление модуля
    @app.route('/modules/delete/<int:id>', methods=['POST'])
    def module_delete(id):
        module = Module.query.get_or_404(id)

        # Удаляем файлы
        if module.photo_path:
            full_path = os.path.join(current_app.root_path,
                                     'static',
                                     module.photo_path)
            if os.path.exists(full_path):
                os.remove(full_path)

        if module.scheme_path:
            full_path = os.path.join(current_app.root_path,
                                     'static',
                                     module.scheme_path)
            if os.path.exists(full_path):
                os.remove(full_path)

        db.session.delete(module)
        db.session.commit()

        flash('Модуль успешно удалён!', 'success')
        return redirect(url_for('modules'))

###############################################################################

    @app.route('/configurator/fittings')
    def fittings():
        fittings = Fitting.query.all()
        return render_template(
            'fittings.html',
            fittings=fittings,
            show_header=True
        )

    @app.route('/fittings/create', methods=['GET', 'POST'])
    def fitting_create():
        if request.method == 'POST':
            name = request.form['name']
            weight = request.form.get('weight', type=float)

            fitting = Fitting(name=name, weight=weight)

            # Сохраняем изображение
            if 'picture' in request.files:
                fitting.path_picture = save_fitting_image(
                    request.files['picture'],
                    name
                )

            db.session.add(fitting)
            db.session.commit()

            flash('Фурнитура успешно создана!', 'success')
            return redirect(url_for('fittings'))

        return render_template(
            'fitting_form.html',
            title='Создать фурнитуру',
            fitting=None
        )

    @app.route('/fittings/edit/<int:id>', methods=['GET', 'POST'])
    def fitting_edit(id):
        fitting = Fitting.query.get_or_404(id)

        if request.method == 'POST':
            old_picture = fitting.path_picture

            fitting.name = request.form['name']
            fitting.weight = request.form.get('weight', type=float)

            # Обновляем изображение
            if 'picture' in request.files:
                fitting.path_picture = save_fitting_image(
                    request.files['picture'],
                    fitting.name,
                    old_picture
                )

            db.session.commit()

            flash('Фурнитура успешно обновлена!', 'success')
            return redirect(url_for('fittings'))

        return render_template(
            'fitting_form.html',
            title='Редактировать фурнитуру',
            fitting=fitting
        )

    @app.route('/fittings/delete/<int:id>', methods=['POST'])
    def fitting_delete(id):
        fitting = Fitting.query.get_or_404(id)

        # Удаляем изображение
        delete_fitting_image(fitting.path_picture)

        db.session.delete(fitting)
        db.session.commit()

        flash('Фурнитура успешно удалена!', 'success')
        return redirect(url_for('fittings'))

    @app.route('/kitchen-types')    # Просмотр всех типов кухни
    def kitchen_types():
        types = KitchenType.query.all()
        return render_template(
            'kitchen_types.html',
            types=types,
            show_header=True
        )

    @app.route('/kitchen-types/create', methods=['GET', 'POST'])
    def kitchen_type_create():
        if request.method == 'POST':
            name = request.form['name']
            short_name = request.form['short_name']

            existing = KitchenType.query.filter_by(
                short_name=short_name
            ).first()
            if existing:
                flash(
                    'Тип кухни с таким коротким именем уже существует!',
                    'error'
                )
                return redirect(url_for('kitchen_type_create'))

            kitchen_type = KitchenType(name=name, short_name=short_name)
            db.session.add(kitchen_type)
            db.session.commit()

            # Создаем папки после успешного сохранения в БД
            success, error = create_kitchen_folders(name)
            if not success:
                flash(
                    f'Тип кухни создан, но не удалось создать папки: {error}',
                    'warning'
                )

            flash('Тип кухни успешно создан!', 'success')
            return redirect(url_for('kitchen_types'))

        return render_template(
            'kitchen_type_form.html',
            title='Создать тип кухни',
            kitchen_type=None
            )

    # Редактирование
    @app.route('/kitchen-types/edit/<int:id>', methods=['GET', 'POST'])
    def kitchen_type_edit(id):
        kitchen_type = KitchenType.query.get_or_404(id)

        if request.method == 'POST':
            old_name = kitchen_type.name
            new_name = request.form['name']

            # Обновляем данные
            kitchen_type.name = new_name
            kitchen_type.short_name = request.form['short_name']
            db.session.commit()

            # Если имя изменилось, переименовываем папки
            if old_name != new_name:
                success, error = rename_kitchen_folders(old_name, new_name)
                if not success:
                    flash(
                        f'Обновлено, но папки не переименованы: {error}',
                        'warning'
                    )

            flash('Тип кухни успешно обновлён!', 'success')
            return redirect(url_for('kitchen_types'))

        return render_template(
            'kitchen_type_form.html',
            title='Редактировать тип кухни',
            kitchen_type=kitchen_type
        )

    # Удаление
    @app.route('/kitchen-types/delete/<int:id>', methods=['POST'])
    def kitchen_type_delete(id):
        kitchen_type = KitchenType.query.get_or_404(id)
        db.session.delete(kitchen_type)
        db.session.commit()

        flash('Тип кухни успешно удалён!', 'success')
        return redirect(url_for('kitchen_types'))

    @app.route('/kitchen_base')
    def kitchen_base():
        bases = KitchenBase.query.all()
        return render_template(
            'kitchen_base.html',
            bases=bases,
            show_header=True)

    @app.route('/kitchen_base/create', methods=['POST'])
    def kitchen_base_create():
        name = request.form.get('kitchen_base')
        base = KitchenBase(kitchen_base=name)
        db.session.add(base)
        db.session.commit()
        return redirect(url_for('kitchen_base'))

    @app.route('/kitchen_base/<int:id>/edit', methods=['POST'])
    def kitchen_base_edit(id):
        base = KitchenBase.query.get(id)
        base.kitchen_base = request.form.get('kitchen_base')
        db.session.commit()
        return redirect(url_for('kitchen_base'))

    @app.route('/kitchen_base/<int:id>/delete', methods=['POST'])
    def kitchen_base_delete(id):
        base = KitchenBase.query.get(id)
        db.session.delete(base)
        db.session.commit()
        return redirect(url_for('kitchen_base'))
