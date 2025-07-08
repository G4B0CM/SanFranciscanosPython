from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from bson import ObjectId
from SanFranciscanos.forms import CertificateForm, DeleteForm
from SanFranciscanos.db import get_mongo_db
import datetime
import io
import os
import csv

bp = Blueprint('certificates', __name__, url_prefix='/certificates')

def get_next_download():
    base_dir = os.path.join(os.getcwd(), 'descargas')
    os.makedirs(base_dir, exist_ok=True)
    existing = [f for f in os.listdir(base_dir) if f.startswith('MatrizCertificados N°')]
    next_number = len(existing) + 1
    return next_number

@bp.route('/')
def index():
    db = get_mongo_db()
    certificates = list(db.certificates.find())

    for cert in certificates:
        student = db.students.find_one({'_id': cert.get('idCatequizado')})
        sacrament = db.sacraments.find_one({'_id': cert.get('idSacramento')})

        cert['nombreCatequizado'] = f"{student.get('firstName', '')} {student.get('lastName', '')}" if student else "No disponible"
        cert['nombreSacramento'] = sacrament.get('name', 'No disponible') if sacrament else "No disponible"

    delete_form = DeleteForm()
    return render_template('documents/list_certificates.html',
                           certificates=certificates,
                           delete_form=delete_form,
                           title="Certificados")

@bp.route('/download')
def download_certificates():
    db = get_mongo_db()
    certificates = list(db.certificates.find())

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Nombre Estudiante', 'ID Estudiante', 'ID feBautismal', 'Sacramento', 'Fecha Emisión', 'Lugar', 'Observaciones'])

    for cert in certificates:
        catequizado = db.students.find_one({'_id': cert.get('idCatequizado')})
        sacramento = db.sacraments.find_one({'_id': cert.get('idSacramento')})
        fe_bautismal = db.feBautismal.find_one({'person_id': str(cert.get('idCatequizado'))})

        nombre = f"{catequizado.get('firstName', '')} {catequizado.get('lastName', '')}" if catequizado else 'No disponible'
        id_estudiante = str(cert.get('idCatequizado'))
        id_febautismal = str(fe_bautismal.get('_id')) if fe_bautismal else 'No disponible'
        sacramento_nombre = sacramento.get('name', 'No disponible') if sacramento else 'No disponible'

        writer.writerow([
            nombre,
            id_estudiante,
            id_febautismal,
            sacramento_nombre,
            cert.get('fechaEmision', ''),
            cert.get('lugar', ''),
            cert.get('observaciones', '')
        ])

    output.seek(0)
    filename = f"MatrizCertificados N° {get_next_download()}.csv"
    return send_file(io.BytesIO(output.getvalue().encode('utf-8')),
                     mimetype='text/csv',
                     as_attachment=True,
                     download_name=filename)

@bp.route('/new', methods=['GET', 'POST'])
def create_certificate():
    db = get_mongo_db()
    form = CertificateForm()

    form.idCatequizado.choices = [(str(p['_id']), f"{p.get('firstName', '')} {p.get('lastName', '')}") for p in db.students.find()]
    form.idSacramento.choices = [(str(s['_id']), s['name']) for s in db.sacraments.find()]

    if request.method == 'POST' and form.validate_on_submit():
        certificate = {
            'idCatequizado': ObjectId(form.idCatequizado.data),
            'idSacramento': ObjectId(form.idSacramento.data),
            'fechaEmision': form.fechaEmision.data,
            'lugar': form.lugar.data,
            'observaciones': form.observaciones.data,
            'createdAt': datetime.datetime.utcnow(),
            'updatedAt': datetime.datetime.utcnow(),
            'state': 'Activo'
        }
        db.certificates.insert_one(certificate)
        flash('Certificado creado exitosamente.', 'success')
        return redirect(url_for('certificates.index'))

    return render_template('documents/certificate_form.html', form=form, title="Nuevo Certificado")

@bp.route('/<id>')
def detail_certificate(id):
    db = get_mongo_db()
    certificate = db.certificates.find_one({'_id': ObjectId(id)})
    if not certificate:
        flash('Certificado no encontrado.', 'danger')
        return redirect(url_for('certificates.index'))

    catequizado = db.students.find_one({'_id': certificate['idCatequizado']})
    sacramento = db.sacraments.find_one({'_id': certificate['idSacramento']})

    return render_template(
        'documents/detail_certificate.html',
        certificate=certificate,
        catequizado_name=f"{catequizado['firstName']} {catequizado['lastName']}" if catequizado else 'No disponible',
        sacramento_name=sacramento['name'] if sacramento else 'No disponible',
        title="Detalle del Certificado"
    )

@bp.route('/edit/<id>', methods=['GET', 'POST'])
def edit_certificate(id):
    db = get_mongo_db()
    certificate = db.certificates.find_one({'_id': ObjectId(id)})
    if not certificate:
        flash('Certificado no encontrado.', 'danger')
        return redirect(url_for('certificates.index'))

    form = CertificateForm(
        idCatequizado=str(certificate['idCatequizado']),
        idSacramento=str(certificate['idSacramento']),
        fechaEmision=certificate['fechaEmision'],
        lugar=certificate['lugar'],
        observaciones=certificate['observaciones']
    )

    form.idCatequizado.choices = [(str(p['_id']), f"{p.get('firstName', '')} {p.get('lastName', '')}") for p in db.students.find()]
    form.idSacramento.choices = [(str(s['_id']), s['name']) for s in db.sacraments.find()]

    if request.method == 'POST' and form.validate_on_submit():
        updates = {
            'idCatequizado': ObjectId(form.idCatequizado.data),
            'idSacramento': ObjectId(form.idSacramento.data),
            'fechaEmision': form.fechaEmision.data,
            'lugar': form.lugar.data,
            'observaciones': form.observaciones.data,
            'updatedAt': datetime.datetime.utcnow()
        }
        db.certificates.update_one({'_id': ObjectId(id)}, {'$set': updates})
        flash('Certificado actualizado correctamente.', 'success')
        return redirect(url_for('certificates.index'))

    return render_template('documents/certificate_form.html', form=form, title="Editar Certificado")

@bp.route('/delete/<id>', methods=['POST'])
def delete_certificate(id):
    db = get_mongo_db()
    db.certificates.delete_one({'_id': ObjectId(id)})
    flash('Certificado eliminado correctamente.', 'success')
    return redirect(url_for('certificates.index'))
