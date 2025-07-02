from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from bson import ObjectId
from datetime import datetime
from SanFranciscanos.forms import AttendanceForm, DeleteForm

bp = Blueprint('Attendances', __name__, url_prefix='/attendances')

@bp.route('/')
def index():
    attendances = list(current_app.mongo_db.attendances.find())
    delete_form = DeleteForm()
    return render_template('attendances/list_attendances.html', attendances=attendances, delete_form=delete_form, title="Asistencias")

@bp.route('/new', methods=['GET', 'POST'])
def new():
    form = AttendanceForm()
    if form.validate_on_submit():
        attendance = {
            'idCurso': form.idCurso.data,
            'idCatequizado': form.idCatequizado.data,
            'date': form.date.data,
            'present': form.present.data,
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow(),
            'state': 'Activo'
        }
        current_app.mongo_db.attendances.insert_one(attendance)
        flash('Asistencia registrada correctamente.', 'success')
        return redirect(url_for('Attendances.index'))
    return render_template('attendances/attendance_form.html', form=form, title="Registrar Asistencia")

@bp.route('/<id>')
def detail(id):
    attendance = current_app.mongo_db.attendances.find_one({'_id': ObjectId(id)})
    if not attendance:
        flash('Registro de asistencia no encontrado.', 'danger')
        return redirect(url_for('Attendances.index'))
    return render_template('attendances/detail_attendance.html', attendance=attendance, title="Detalle de Asistencia")

@bp.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    attendance = current_app.mongo_db.attendances.find_one({'_id': ObjectId(id)})
    if not attendance:
        flash('Registro no encontrado.', 'danger')
        return redirect(url_for('Attendances.index'))

    form = AttendanceForm(data=attendance)

    if form.validate_on_submit():
        updates = {
            'idCurso': form.idCurso.data,
            'idCatequizado': form.idCatequizado.data,
            'date': form.date.data,
            'present': form.present.data,
            'updatedAt': datetime.utcnow()
        }
        current_app.mongo_db.attendances.update_one({'_id': ObjectId(id)}, {'$set': updates})
        flash('Asistencia actualizada correctamente.', 'success')
        return redirect(url_for('Attendances.index'))

    return render_template('attendances/attendance_form.html', form=form, title="Editar Asistencia")

@bp.route('/delete/<id>', methods=['POST'])
def delete(id):
    current_app.mongo_db.attendances.delete_one({'_id': ObjectId(id)})
    flash('Registro eliminado.', 'success')
    return redirect(url_for('Attendances.index'))
