from flask import Blueprint, render_template, request, redirect, url_for, flash
from bson import ObjectId
from datetime import datetime
from SanFranciscanos.forms import DataSheetForm, DeleteForm
from SanFranciscanos.db import get_mongo_db

bp = Blueprint('documents', __name__, url_prefix='/documents')


@bp.route('/datasheet')
def list_datasheets():
    db = get_mongo_db()
    datasheets = list(db.datasheets.find())

    for ds in datasheets:
        institution = db.institutions.find_one({'_id': ds.get('ds_idInstitution')})
        level = db.levels.find_one({'_id': ds.get('ds_idLevel')})
        certificate = db.certificates.find_one({'_id': ds.get('ds_idCertificate')})
        person = db.persons.find_one({'_id': ds.get('person_id')})

        ds['institution_name'] = institution['name'] if institution else 'No disponible'
        ds['level_name'] = level['name'] if level else 'No disponible'
        ds['certificate_info'] = certificate.get('lugar', 'Sin lugar') if certificate else 'No disponible'
        ds['person_name'] = f"{person.get('name', '')} {person.get('surname', '')}" if person else 'No disponible'

    delete_form = DeleteForm()
    return render_template('documents/list_datasheets.html',
                           datasheets=datasheets,
                           delete_form=delete_form,
                           title="Fichas de Catequizados")


@bp.route('/')
def index():
    # Por ahora puede redirigir al formulario de ficha
    return redirect(url_for('documents.create_datasheet'))

@bp.route('/datasheet/new', methods=['GET', 'POST'])
def create_datasheet():
    db = get_mongo_db()
    form = DataSheetForm()

    # Cargar listas con nombres legibles
    form.ds_idInstitution.choices = [(str(i['_id']), i.get('name', 'Sin nombre')) for i in db.institutions.find()]
    form.ds_idLevel.choices = [(str(l['_id']), l.get('name', 'Sin nombre')) for l in db.levels.find()]
    form.ds_idCertificate.choices = [(str(c['_id']), f"{c.get('lugar', 'Lugar desconocido')} - {c.get('fechaEmision', '')}") for c in db.certificates.find()]
    
    # Solo mostrar personas con rol "Catequizado"
    form.person_id.choices = [(str(p['_id']), f"{p.get('name', '')} {p.get('surname', '')}") for p in db.persons.find({'role': 'Catequizado'})]

    if form.validate_on_submit():
        datasheet = {
            'person_id': ObjectId(form.person_id.data) if form.person_id.data else None,
            'ds_idInstitution': ObjectId(form.ds_idInstitution.data) if form.ds_idInstitution.data else None,
            'ds_idCertificate': ObjectId(form.ds_idCertificate.data) if form.ds_idCertificate.data else None,
            'ds_idLevel': ObjectId(form.ds_idLevel.data) if form.ds_idLevel.data else None,
            'ds_fechaRegistro': form.ds_fechaRegistro.data,
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow()
        }

        db.datasheets.insert_one(datasheet)
        flash('Ficha creada exitosamente.', 'success')
        return redirect(url_for('documents.list_datasheets'))

    return render_template('documents/data_sheet_form.html', form=form, title="Nueva Ficha de Catequizado")
