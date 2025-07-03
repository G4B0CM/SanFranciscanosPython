from flask import Blueprint, render_template, request, redirect, url_for, flash
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime
from SanFranciscanos.forms import DocumentForm, DeleteForm, DataSheetForm
from SanFranciscanos.db import get_mongo_db

bp = Blueprint('documents', __name__, url_prefix='/documents')


@bp.route('/')
def index():
    db = get_mongo_db()
    documents = list(db.documents.find())
    delete_form = DeleteForm()
    return render_template('documents/list_documents.html', documents=documents, delete_form=delete_form, title="Documentos")


@bp.route('/new', methods=['GET', 'POST'])
def new():
    form = DocumentForm()
    if form.validate_on_submit():
        db = get_mongo_db()
        document = {
            'name': form.name.data,
            'type': form.type.data,
            'description': form.description.data,
            'category': form.category.data,
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow(),
            'state': 'Activo'
        }
        db.documents.insert_one(document)
        flash('Documento creado exitosamente.', 'success')
        return redirect(url_for('documents.index'))

    return render_template('documents/document_form.html', form=form, title="Nuevo Documento")


@bp.route('/<id>')
def detail(id):
    db = get_mongo_db()
    try:
        document = db.documents.find_one({'_id': ObjectId(id)})
    except InvalidId:
        flash('ID inválido.', 'danger')
        return redirect(url_for('documents.index'))

    if not document:
        flash('Documento no encontrado.', 'danger')
        return redirect(url_for('documents.index'))

    return render_template('documents/detail_document.html', document=document, title="Detalle del Documento")


@bp.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    db = get_mongo_db()
    try:
        document = db.documents.find_one({'_id': ObjectId(id)})
    except InvalidId:
        flash('ID inválido.', 'danger')
        return redirect(url_for('documents.index'))

    if not document:
        flash('Documento no encontrado.', 'danger')
        return redirect(url_for('documents.index'))

    form = DocumentForm(data=document)

    if form.validate_on_submit():
        updates = {
            'name': form.name.data,
            'type': form.type.data,
            'description': form.description.data,
            'category': form.category.data,
            'updatedAt': datetime.utcnow()
        }
        db.documents.update_one({'_id': ObjectId(id)}, {'$set': updates})
        flash('Documento actualizado exitosamente.', 'success')
        return redirect(url_for('documents.index'))

    return render_template('documents/document_form.html', form=form, title="Editar Documento")


@bp.route('/delete/<id>', methods=['POST'])
def delete(id):
    db = get_mongo_db()
    try:
        db.documents.delete_one({'_id': ObjectId(id)})
        flash('Documento eliminado correctamente.', 'success')
    except InvalidId:
        flash('ID inválido.', 'danger')
    return redirect(url_for('documents.index'))


@bp.route('/new_data_sheet', methods=['GET', 'POST'])
def new_data_sheet():
    db = get_mongo_db()
    form = DataSheetForm()

    if form.validate_on_submit():
        data_sheet = {
            "c_firstName": form.c_firstName.data,
            "c_secondName": form.c_secondName.data,
            "c_lastName": form.c_lastName.data,
            "c_secondLastName": form.c_secondLastName.data,
            "c_sex": form.c_sex.data,
            "c_birthdate": form.c_birthdate.data,
            "ds_sonNumbr": form.ds_sonNumbr.data,
            "ds_numbrBrothers": form.ds_numbrBrothers.data,
            "ds_livesWith": form.ds_livesWith.data,
            "ds_residentialPhone": form.ds_residentialPhone.data,
            "ds_mainAddress": form.ds_mainAddress.data,
            "c_bloodType": form.c_bloodType.data,
            "c_alergies": form.c_alergies.data,
            "c_emergencyContactName": form.c_emergencyContactName.data,
            "c_emergencyContactPhone": form.c_emergencyContactPhone.data,
            "c_details": form.c_details.data,
            "c_idInstitution": ObjectId(form.c_idInstitution.data) if form.c_idInstitution.data else None,

            "f_firstName": form.f_firstName.data,
            "f_secondName": form.f_secondName.data,
            "f_lastName": form.f_lastName.data,
            "f_secondLastName": form.f_secondLastName.data,
            "f_ocupation": form.f_ocupation.data,
            "f_phoneContact": form.f_phoneContact.data,
            "f_emailContact": form.f_emailContact.data,

            "m_firstName": form.m_firstName.data,
            "m_secondName": form.m_secondName.data,
            "m_lastName": form.m_lastName.data,
            "m_secondLastName": form.m_secondLastName.data,
            "m_ocupation": form.m_ocupation.data,
            "m_phoneContact": form.m_phoneContact.data,
            "m_emailContact": form.m_emailContact.data,

            "ds_idInstitution": ObjectId(form.ds_idInstitution.data) if form.ds_idInstitution.data else None,
            "ds_idCertificate": ObjectId(form.ds_idCertificate.data) if form.ds_idCertificate.data else None,
            "ds_idLevel": ObjectId(form.ds_idLevel.data) if form.ds_idLevel.data else None,
            "ds_schoolsName": form.ds_schoolsName.data,
            "ds_schoolGrade": form.ds_schoolGrade.data,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
            "state": "Activo"
        }

        db.data_sheets.insert_one(data_sheet)
        flash('Ficha de datos creada exitosamente.', 'success')
        return redirect(url_for('documents.index'))

    # Carga de opciones
    institutions = list(db.institutions.find())
    certificates = list(db.certificates.find())
    levels = list(db.levels.find())

    form.c_idInstitution.choices = [(str(i['_id']), i['name']) for i in institutions]
    form.ds_idInstitution.choices = [(str(i['_id']), i['name']) for i in institutions]
    form.ds_idCertificate.choices = [(str(i['_id']), i['name']) for i in certificates]
    form.ds_idLevel.choices = [(str(i['_id']), i['name']) for i in levels]

    return render_template('documents/data_sheet_form.html', form=form, title="Nueva Ficha del Catequizando")


@bp.route('/data_sheets/edit/<id>', methods=['GET', 'POST'])
def update_data_sheet(id):
    db = get_mongo_db()
    try:
        datasheet = db.data_sheets.find_one({'_id': ObjectId(id)})
    except InvalidId:
        flash("ID inválido", "danger")
        return redirect(url_for('documents.list_data_sheets'))

    if not datasheet:
        flash("Ficha no encontrada", "danger")
        return redirect(url_for('documents.list_data_sheets'))

    form = DataSheetForm(data=datasheet)

    institutions = list(db.institutions.find())
    certificates = list(db.certificates.find())
    levels = list(db.levels.find())

    form.c_idInstitution.choices = [(str(i['_id']), i['name']) for i in institutions]
    form.ds_idInstitution.choices = [(str(i['_id']), i['name']) for i in institutions]
    form.ds_idCertificate.choices = [(str(i['_id']), i['name']) for i in certificates]
    form.ds_idLevel.choices = [(str(i['_id']), i['name']) for i in levels]

    if form.validate_on_submit():
        update_data = {
            "c_firstName": form.c_firstName.data,
            "c_secondName": form.c_secondName.data,
            "c_lastName": form.c_lastName.data,
            "c_secondLastName": form.c_secondLastName.data,
            "c_sex": form.c_sex.data,
            "c_birthdate": form.c_birthdate.data,
            "ds_sonNumbr": form.ds_sonNumbr.data,
            "ds_numbrBrothers": form.ds_numbrBrothers.data,
            "ds_livesWith": form.ds_livesWith.data,
            "ds_residentialPhone": form.ds_residentialPhone.data,
            "ds_mainAddress": form.ds_mainAddress.data,
            "c_bloodType": form.c_bloodType.data,
            "c_alergies": form.c_alergies.data,
            "c_emergencyContactName": form.c_emergencyContactName.data,
            "c_emergencyContactPhone": form.c_emergencyContactPhone.data,
            "c_details": form.c_details.data,
            "c_idInstitution": ObjectId(form.c_idInstitution.data) if form.c_idInstitution.data else None,

            "f_firstName": form.f_firstName.data,
            "f_secondName": form.f_secondName.data,
            "f_lastName": form.f_lastName.data,
            "f_secondLastName": form.f_secondLastName.data,
            "f_ocupation": form.f_ocupation.data,
            "f_phoneContact": form.f_phoneContact.data,
            "f_emailContact": form.f_emailContact.data,

            "m_firstName": form.m_firstName.data,
            "m_secondName": form.m_secondName.data,
            "m_lastName": form.m_lastName.data,
            "m_secondLastName": form.m_secondLastName.data,
            "m_ocupation": form.m_ocupation.data,
            "m_phoneContact": form.m_phoneContact.data,
            "m_emailContact": form.m_emailContact.data,

            "ds_idInstitution": ObjectId(form.ds_idInstitution.data) if form.ds_idInstitution.data else None,
            "ds_idCertificate": ObjectId(form.ds_idCertificate.data) if form.ds_idCertificate.data else None,
            "ds_idLevel": ObjectId(form.ds_idLevel.data) if form.ds_idLevel.data else None,
            "ds_schoolsName": form.ds_schoolsName.data,
            "ds_schoolGrade": form.ds_schoolGrade.data,
            "updatedAt": datetime.utcnow()
        }

        db.data_sheets.update_one({'_id': ObjectId(id)}, {'$set': update_data})
        flash("Ficha actualizada exitosamente", "success")
        return redirect(url_for('documents.detail_data_sheet', id=id))

    return render_template('documents/data_sheet_form.html', form=form, title="Editar Ficha")


@bp.route('/data_sheet/<id>')
def detail_data_sheet(id):
    db = get_mongo_db()
    try:
        datasheet = db.data_sheets.find_one({'_id': ObjectId(id)})
    except InvalidId:
        flash('ID inválido.', 'danger')
        return redirect(url_for('documents.index'))

    if not datasheet:
        flash('Ficha no encontrada.', 'danger')
        return redirect(url_for('documents.index'))

    return render_template('documents/detail_data_sheet.html', datasheet=datasheet, title="Detalle Ficha")


@bp.route('/delete_data_sheet/<id>', methods=['POST'])
def delete_data_sheet(id):
    db = get_mongo_db()
    try:
        db.data_sheets.delete_one({'_id': ObjectId(id)})
        flash('Ficha eliminada exitosamente.', 'success')
    except InvalidId:
        flash('ID inválido.', 'danger')
    return redirect(url_for('documents.index'))


@bp.route('/data_sheets')
def list_data_sheets():
    db = get_mongo_db()
    data_sheets = list(db.data_sheets.find())
    return render_template('documents/list_data_sheets.html', data_sheets=data_sheets, title="Fichas Registradas")
