import os

class Config:
    # Путь к базе данных (base.db3 лежит в корне проекта)
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(BASE_DIR, "base.db3")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'tyap-lyap-secret-key-2026'  # добавь эту строку