from flask import Flask
import os, json, locale
from . import db  
from flask_moment import Moment

def create_app():
    app = Flask(__name__)
    moment = Moment(app)

    try:
        locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_ALL, 'Spanish_Spain.1252')
        except locale.Error:
            print("Advertencia: No se pudo establecer la configuración regional a es_ES.")

    ruta_config = os.path.join(os.path.dirname(__file__), '..', 'config.json')
    with open(ruta_config, 'r') as archivo_config:
        config = json.load(archivo_config)

    app.config['SECRET_KEY'] = config['secret_key']
    NAME_SERVER = config['name_server']
    DATABASE = config['database']
    USERNAME = config.get('username')
    PASSWORD = config.get('password')

    if USERNAME and PASSWORD:
        CONNECTION_STRING = (
            f"mssql+pyodbc://{USERNAME}:{PASSWORD}@{NAME_SERVER}/{DATABASE}?"
            f"driver=ODBC+Driver+17+for+SQL+Server"
            "&TrustServerCertificate=yes"
            "&charset=utf8"  # <-- AÑADIR ESTA LÍNEA
        )
    else:
        CONNECTION_STRING = (
            f"mssql+pyodbc://@{NAME_SERVER}/{DATABASE}?"
            f"driver=ODBC+Driver+17+for+SQL+Server"
            "&Trusted_Connection=yes"
            "&TrustServerCertificate=yes"
            "&charset=utf8"  # <-- AÑADIR ESTA LÍNEA
        )

    print(f"Intentando conectar con: {CONNECTION_STRING.replace(PASSWORD, '****') if PASSWORD else CONNECTION_STRING}")
    
    try:
        db.init_engine(CONNECTION_STRING)
        with db.engine.connect() as conn:
            print("Conexión a la base de datos exitosa.")
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        raise

    # Puedes agregar si quieres:
    app.engine = db.engine
    app.SessionLocal = db.SessionLocal

    # Registrar Blueprints
    from . import documents, persons, institutions, sacraments, levels, home, enrollment, onboarding
    app.register_blueprint(enrollment.bp)
    app.register_blueprint(documents.bp)
    app.register_blueprint(persons.bp)
    app.register_blueprint(institutions.bp)
    app.register_blueprint(sacraments.bp)
    app.register_blueprint(levels.bp)
    app.register_blueprint(home.bp)
    from . import onboarding
    app.register_blueprint(onboarding.bp)

    return app