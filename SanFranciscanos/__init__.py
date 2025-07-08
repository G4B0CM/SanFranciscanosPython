import os
import json
import locale
from flask import Flask
from .db import init_db

def create_app():
    app = Flask(__name__, template_folder='templates')

    # Establecer configuración regional a español
    try:
        locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_ALL, 'Spanish_Spain.1252')
        except locale.Error:
            print("No se pudo establecer configuración regional a Español.")

    # Cargar configuración desde config.json
    ruta_config = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config.json'))
    with open(ruta_config, 'r') as archivo_config:
        config = json.load(archivo_config)

    # Validación de claves necesarias
    if 'mongo_uri' not in config or 'mongo_db' not in config:
        raise KeyError("Faltan las claves 'mongo_uri' y/o 'mongo_db' en config.json")

    # Configuración Flask
    app.config['SECRET_KEY'] = config.get('secret_key', 'clave_por_defecto')
    app.config['mongo_uri'] = config['mongo_uri']
    app.config['mongo_db'] = config['mongo_db']

    print(f"[CONFIG] Base MongoDB: {app.config['mongo_db']}")

    # Inicializar MongoDB
    init_db(app)

    # === Registro de Blueprints ===
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
