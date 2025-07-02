from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from bson import ObjectId
from SanFranciscanos.forms import InstitutionForm, DeleteForm
import datetime

bp = Blueprint('Institutions', __name__, url_prefix='/institutions')

@bp.route('/')
def index():
    institutions = list(current_app.mongo_db.institutions.find())
    delete_form = DeleteForm()
    return render_template('institutions/list_institutions.html', institutions=institutions, delete_form=delete_form, title="Instituciones")

@bp.route('/new', methods=['GET', 'POST'])
def new():
    form = InstitutionForm()
    if form.validate_on_submit():
        institution = {
            'name': form.name.data,
            'type': form.type.data,
            'location': form.location.data,
            'contact': form.contact.data,
            'createdAt': datetime.datetime.utcnow(),
            'updatedAt': datetime.datetime.utcnow(),
            'state': 'Activo'
        }
        current_app.mongo_db.institutions.insert_one(institution)
        flash('Institución creada exitosamente.', 'success')
        return redirect(url_for('Institutions.index'))
    return render_template('institutions/institution_form.html', form=form, title="Nueva Institución")

@bp.route('/<id>')
def detail(id):
    institution = current_app.mongo_db.institutions.find_one({'_id': ObjectId(id)})
    if not institution:
        flash('Institución no encontrada.', 'danger')
        return redirect(url_for('Institutions.index'))
    return render_template('institutions/detail_institution.html', institution=institution, title="Detalle de Institución")

@bp.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    institution = current_app.mongo_db.institutions.find_one({'_id': ObjectId(id)})
    if not institution:
        flash('Institución no encontrada.', 'danger')
        return redirect(url_for('Institutions.index'))

    form = InstitutionForm(data=institution)

    if form.validate_on_submit():
        updates = {
            'name': form.name.data,
            'type': form.type.data,
            'location': form.location.data,
            'contact': form.contact.data,
            'updatedAt': datetime.datetime.utcnow()
        }
        current_app.mongo_db.institutions.update_one({'_id': ObjectId(id)}, {'$set': updates})
        flash('Institución actualizada exitosamente.', 'success')
        return redirect(url_for('Institutions.index'))

    return render_template('institutions/institution_form.html', form=form, title="Editar Institución")

@bp.route('/delete/<id>', methods=['POST'])
def delete(id):
    current_app.mongo_db.institutions.delete_one({'_id': ObjectId(id)})
    flash('Institución eliminada correctamente.', 'success')
    return redirect(url_for('Institutions.index'))
