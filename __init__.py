from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    import locale
    locale.setlocale(locale.LC_ALL,'es_ES')

    app.config.from_object('config.Config')
    db.init_app(app)

    from .modelos import Catequizado, Person, Institution

    with app.app_context():
        db.create_all()
    
    return app