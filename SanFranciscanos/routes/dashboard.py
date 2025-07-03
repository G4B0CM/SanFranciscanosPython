from flask import Blueprint, render_template
from SanFranciscanos.db import get_mongo_db

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@bp.route('/')
def index():
    db = get_mongo_db()

    # Roles a considerar
    roles = ['Catequizado', 'PadreMadre', 'Padrino', 'Ayudante', 'Catequista', 'Eclesiastico']
    roles_data = {r: db.persons.count_documents({'role': r}) for r in roles}

    # Tipos de institución
    tipos_institucion = db.institutions.distinct('tipo')
    tipos_data = {tipo.capitalize(): db.institutions.count_documents({'tipo': tipo}) for tipo in tipos_institucion}

    # Otros conteos
    stats = {
        'Catequizados': roles_data.get('Catequizado', 0),
        'Padres o Madres': roles_data.get('PadreMadre', 0),
        'Padrinos': roles_data.get('Padrino', 0),
        'Ayudantes': roles_data.get('Ayudante', 0),
        'Catequistas': roles_data.get('Catequista', 0),
        'Eclesiásticos': roles_data.get('Eclesiastico', 0),
        'Instituciones': sum(tipos_data.values()),
        'Cursos': db.courses.count_documents({}),
        'Grupos': db.groups.count_documents({}),
        'Asistencias': db.attendances.count_documents({}),
        'Certificados': db.certificates.count_documents({}),
        'Documentos': db.documents.count_documents({}),
        'Sacramentos': db.sacraments.count_documents({}),
        'Niveles': db.levels.count_documents({})
    }

    return render_template('dashboard/index.html',
                           stats=stats,
                           roles_data=roles_data,
                           tipos_institucion=tipos_data)
