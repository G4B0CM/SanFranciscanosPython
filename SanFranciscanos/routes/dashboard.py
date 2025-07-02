from flask import Blueprint, render_template, current_app
from bson.objectid import ObjectId

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@bp.route('/')
def index():
    mongo = current_app.mongo_db

    stats = {
        'total_catequizados': mongo.catequizados.count_documents({}),
        'total_padres': mongo.padresmadres.count_documents({}),
        'total_padrinos': mongo.padrinos.count_documents({}),
        'total_ayudantes': mongo.ayudantes.count_documents({}),
        'total_catequistas': mongo.catequistas.count_documents({}),
        'total_instituciones': mongo.institutions.count_documents({}),
        'total_cursos': mongo.courses.count_documents({}),
        'total_grupos': mongo.groups.count_documents({}),
        'total_asistencias': mongo.attendances.count_documents({}),
        'total_certificados': mongo.certificates.count_documents({}),
        'total_documentos': mongo.documents.count_documents({}),
        'total_sacramentos': mongo.sacraments.count_documents({}),
        'total_niveles': mongo.levels.count_documents({})
    }

    return render_template('dashboard/index.html', stats=stats)
