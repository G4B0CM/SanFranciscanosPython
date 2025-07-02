import os
import json
import locale
from flask import Flask
from flask_pymongo import PyMongo
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from . import models as md

mongo = PyMongo()

def create_app():
    app = Flask(__name__)

    # ───────────────────────────────
    # CONFIGURACIÓN DE LOCALIZACIÓN
    # ───────────────────────────────
    try:
        locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_ALL, 'Spanish_Spain.1252')
        except locale.Error:
            print("No se pudo establecer configuración regional a Español.")

    # ───────────────────────────────
    # CARGA DE CONFIGURACIÓN
    # ───────────────────────────────
    ruta_config = os.path.join(os.path.dirname(__file__), '..', 'config.json')
    with open(ruta_config, 'r') as archivo_config:
        config = json.load(archivo_config)

    # Clave secreta Flask
    app.config['SECRET_KEY'] = config['secret_key']

    # ───────────────────────────────
    # CONFIGURACIÓN DE SQL SERVER
    # ───────────────────────────────
    NAME_SERVER = config['name_server']
    DATABASE    = config['database']
    USERNAME    = config.get('username')
    PASSWORD    = config.get('password')
    DRIVER      = config['controlador_odbc']

    if USERNAME and PASSWORD:
        conn_str = (
            f"mssql+pyodbc://{USERNAME}:{PASSWORD}@{NAME_SERVER}/{DATABASE}?"
            f"driver={DRIVER}&TrustServerCertificate=yes"
        )
    else:
        conn_str = (
            f"mssql+pyodbc://@{NAME_SERVER}/{DATABASE}?"
            f"driver={DRIVER}&Trusted_Connection=yes&TrustServerCertificate=yes"
        )

    engine = create_engine(conn_str, echo=False, future=True)
    app.engine = engine
    app.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    try:
        with engine.connect():
            print("Conectado a SQL Server")
    except Exception as e:
        print(f"Error al conectar a SQL Server: {e}")

    # ───────────────────────────────
    # CONFIGURACIÓN DE MONGODB
    # ───────────────────────────────
    app.config["MONGO_URI"] = f"{config['mongo_uri']}/{config['mongo_db']}"
    mongo.init_app(app)
    app.mongo_db = mongo.db  # Esto te da acceso directo vía current_app.mongo_db
    print(f"✅ Conectado a MongoDB en {app.config['MONGO_URI']}")

    # ───────────────────────────────
    # IMPORTAR Y REGISTRAR RUTAS
    # ───────────────────────────────
    from .routes.auth         import bp as auth_bp
    from .routes.home         import bp as home_bp
    from .routes.documents    import bp as documents_bp
    from .routes.certificates import bp as certificates_bp
    from .routes.attendances  import bp as attendances_bp
    from .routes.courses      import bp as courses_bp
    from .routes.groups       import bp as groups_bp
    from .routes.institutions import bp as institutions_bp
    from .routes.levels       import bp as levels_bp
    from .routes.persons      import bp as persons_bp
    from .routes.students     import bp as students_bp
    from .routes.sacraments   import bp as sacraments_bp
    from .routes.dashboard    import bp as dashboard_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(certificates_bp)
    app.register_blueprint(attendances_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(groups_bp)
    app.register_blueprint(institutions_bp)
    app.register_blueprint(levels_bp)
    app.register_blueprint(persons_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(sacraments_bp)
    app.register_blueprint(dashboard_bp)

    return app
