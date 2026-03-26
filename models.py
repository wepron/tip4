from extensions import db
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
