from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from SanFranciscanos import models as md
import json
import os

def create_app():
    app = Flask(__name__)

    import locale
    locale.setlocale(locale.LC_ALL, 'es_ES')

    ruta_config = os.path.join(os.path.dirname(__file__), '..', 'config.json')

    with open(ruta_config, 'r') as archivo_config:
        config = json.load(archivo_config)

    NAME_SERVER = config['name_server']
    DATABASE = config['database']
    USERNAME = config['username']
    PASSWORD = config['password']
    CONTROLLER_ODBC = config['controlador_odbc']

    # 4. Crear Cadena de Conexión (con login SQL)
    CONNECTION_STRING = f"mssql+pyodbc://@{NAME_SERVER}/{DATABASE}?driver=ODBC+Driver+17+for+SQL+Server"
    "&Trusted_Connection=yes&TrustedServerCertificate=yes"
    engine = create_engine(CONNECTION_STRING)

    # Crea las tablas
    md.Base.metadata.create_all(engine)

    # Opcional: puedes guardar el engine o session factory en el app context
    app.engine = engine
    app.SessionLocal = sessionmaker(bind=engine)

    from . import home
    app.register_blueprint(home.bp)

    return app
