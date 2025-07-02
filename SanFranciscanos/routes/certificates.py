from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from bson import ObjectId
from SanFranciscanos.forms import CertificateForm, DeleteForm
import datetime

bp = Blueprint('Certificates', __name__, url_prefix='/certificates')

@bp.route('/')
def index():
    certificates = list(current_app.mongo_db.certificates.find())
    delete_form = DeleteForm()
    return render_template('Documents/list_certificates.html', certificates=certificates, delete_form=delete_form, title="Certificados")

@bp.route('/new', methods=['GET', 'POST'])
def create_certificate():
    form = CertificateForm()
    if form.validate_on_submit():
        certificate = {
            'idCatequizado': form.idCatequizado.data,
            'idSacramento': form.idSacramento.data,
            'fechaEmision': form.fechaEmision.data,
            'lugar': form.lugar.data,
            'observaciones': form.observaciones.data,
            'createdAt': datetime.datetime.utcnow(),
            'updatedAt': datetime.datetime.utcnow(),
            'state': 'Activo'
        }
        current_app.mongo_db.certificates.insert_one(certificate)
        flash('Certificado creado exitosamente.', 'success')
        return redirect(url_for('Certificates.index'))
    return render_template('Documents/certificate_form.html', form=form, title="Nuevo Certificado")

@bp.route('/<id>')
def detail_certificate(id):
    certificate = current_app.mongo_db.certificates.find_one({'_id': ObjectId(id)})
    if not certificate:
        flash('Certificado no encontrado.', 'danger')
        return redirect(url_for('Certificates.index'))
    return render_template('Documents/detail_certificate.html', certificate=certificate)

@bp.route('/edit/<id>', methods=['GET', 'POST'])
def edit_certificate(id):
    certificate = current_app.mongo_db.certificates.find_one({'_id': ObjectId(id)})
    if not certificate:
        flash('Certificado no encontrado.', 'danger')
        return redirect(url_for('Certificates.index'))

    form = CertificateForm(data=certificate)

    if form.validate_on_submit():
        updates = {
            'idCatequizado': form.idCatequizado.data,
            'idSacramento': form.idSacramento.data,
            'fechaEmision': form.fechaEmision.data,
            'lugar': form.lugar.data,
            'observaciones': form.observaciones.data,
            'updatedAt': datetime.datetime.utcnow()
        }
        current_app.mongo_db.certificates.update_one({'_id': ObjectId(id)}, {'$set': updates})
        flash('Certificado actualizado correctamente.', 'success')
        return redirect(url_for('Certificates.index'))

    return render_template('Documents/certificate_form.html', form=form, title="Editar Certificado")

@bp.route('/delete/<id>', methods=['POST'])
def delete_certificate(id):
    current_app.mongo_db.certificates.delete_one({'_id': ObjectId(id)})
    flash('Certificado eliminado correctamente.', 'success')
    return redirect(url_for('Certificates.index'))
