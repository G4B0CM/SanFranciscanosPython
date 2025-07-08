from flask import Blueprint, render_template, request, redirect, url_for, flash
from bson.objectid import ObjectId
from SanFranciscanos.db import get_mongo_db
from SanFranciscanos.forms import AttendanceForm, DeleteForm

bp = Blueprint('attendances', __name__, url_prefix='/attendances')


@bp.route('/')
def list_attendances():
    db = get_mongo_db()
    attendances = list(db.attendances.find())
    delete_form = DeleteForm()
    return render_template('attendances/list_attendances.html', attendances=attendances, delete_form=delete_form, title="Lista de Asistencias")


@bp.route('/create', methods=['GET', 'POST'])
def create_attendances():
    db = get_mongo_db()
    form = AttendanceForm()
    if form.validate_on_submit():
        db.attendances.insert_one({
            "student_id": form.student_id.data,
            "course_id": form.course_id.data,
            "date": str(form.date.data),
            "status": form.status.data
        })
        flash("Asistencia registrada correctamente.", "success")
        return redirect(url_for('attendances.list_attendances'))
    return render_template('attendances/attendance_form.html', form=form, title="Registrar Asistencia")


@bp.route('/edit/<id>', methods=['GET', 'POST'])
def edit_attendances(id):
    db = get_mongo_db()
    item = db.attendances.find_one({"_id": ObjectId(id)})
    if not item:
        flash("Registro de asistencia no encontrado.", "danger")
        return redirect(url_for('attendances_bp.list_attendances'))

    form = AttendanceForm(data=item)
    if form.validate_on_submit():
        db.attendances.update_one(
            {"_id": ObjectId(id)},
            {"$set": {
                "student_id": form.student_id.data,
                "course_id": form.course_id.data,
                "date": str(form.date.data),
                "status": form.status.data
            }}
        )
        flash("Asistencia actualizada correctamente.", "success")
        return redirect(url_for('attendances.list_attendances'))

    return render_template('attendances/attendance_form.html', form=form, title="Editar Asistencia")


@bp.route('/detail/<id>')
def detail_attendances(id):
    db = get_mongo_db()
    item = db.attendances.find_one({"_id": ObjectId(id)})
    if not item:
        flash("Registro no encontrado.", "warning")
        return redirect(url_for('attendances.list_attendances'))
    return render_template('attendances/detail_attendance.html', attendance=item, title="Detalle de Asistencia")


@bp.route('/delete/<id>', methods=['POST'])
def delete_attendances(id):
    db = get_mongo_db()
    result = db.attendances.delete_one({"_id": ObjectId(id)})
    if result.deleted_count:
        flash("Asistencia eliminada correctamente.", "success")
    else:
        flash("No se pudo eliminar el registro.", "danger")
    return redirect(url_for('attendances.list_attendances'))
