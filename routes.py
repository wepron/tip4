from flask import render_template, request, redirect, url_for, flash
from models import Color, Fitting, KitchenType, KitchenBase
from extensions import db

# Убираем secure_filename из импорта, так как она уже есть в utils
from utils import (
    save_fitting_image,
    delete_fitting_image,
    create_kitchen_folders,
    rename_kitchen_folders
)


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

    @app.route('/configurator/modules')
    def modules():
        return render_template('modules.html', show_header=True)

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
