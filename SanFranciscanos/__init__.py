import os
import json
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from . import models as md # Asumiendo que tus modelos están en models.py

def create_app():
    app = Flask(__name__)

    import locale
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
        # Conexión con autenticación SQL Server
        CONNECTION_STRING = (
            f"mssql+pyodbc://{USERNAME}:{PASSWORD}@{NAME_SERVER}/{DATABASE}?"
            f"driver=ODBC+Driver+17+for+SQL+Server"
            # "&Trusted_Connection=no" 
            "&TrustServerCertificate=yes" 
        )
    else:
        # Conexión con autenticación de Windows (Trusted Connection)
        CONNECTION_STRING = (
            f"mssql+pyodbc://@{NAME_SERVER}/{DATABASE}?"
            f"driver=ODBC+Driver+17+for+SQL+Server"
            "&Trusted_Connection=yes"
            "&TrustServerCertificate=yes"
        )

    print(f"Intentando conectar con: {CONNECTION_STRING.replace(PASSWORD, '****') if PASSWORD else CONNECTION_STRING}")

    try:
        engine = create_engine(CONNECTION_STRING)
        with engine.connect() as connection:
            print("Conexión a la base de datos exitosa.")
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        raise

    app.engine = engine
    app.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Registrar Blueprints
    from . import routes 
    app.register_blueprint(routes.bp)

    
    from . import home
    app.register_blueprint(home.bp)

    return app
