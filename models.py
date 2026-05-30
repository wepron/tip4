from extensions import db
from sqlalchemy import CheckConstraint
# from sqlalchemy import text


class Color(db.Model):
    __tablename__ = 'colors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    short_name = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<Color {self.name}>'


class Fitting(db.Model):
    __tablename__ = 'fittings'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    path_picture = db.Column(db.String(500))
    weight = db.Column(db.Float)  # вещественное число

    def __repr__(self):
        return f'<Fitting {self.name}>'


class KitchenType(db.Model):
    __tablename__ = 'kitchen_types'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    short_name = db.Column(db.String(50), nullable=False, unique=True)

    def __repr__(self):
        return f'<KitchenType {self.short_name}>'


class KitchenBase(db.Model):
    __tablename__ = 'kitchen_bases'

    id = db.Column(db.Integer, primary_key=True)
    kitchen_base = db.Column(db.String(100), nullable=False, unique=True)


class Module(db.Model):
    __tablename__ = 'modules'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    short_name = db.Column(db.String(200), nullable=False)
    scheme_path = db.Column(db.String(500))
    photo_path = db.Column(db.String(500))

    # Внешние ключи
    kitchen_base_id = db.Column(db.Integer,
                                db.ForeignKey('kitchen_bases.id'),
                                nullable=False)

    kitchen_type_id = db.Column(db.Integer,
                                db.ForeignKey('kitchen_types.id'),
                                nullable=False)

    boxes = db.Column(db.Integer,
                      CheckConstraint('boxes >= 0'),
                      nullable=False)

    kitchen_type = db.relationship('KitchenType', backref='modules')

    def __repr__(self):
        return f'<Module {self.name}>'
