from flask import Blueprint, render_template, request, redirect, url_for, flash
from bson.objectid import ObjectId
from SanFranciscanos.forms import StudentForm, DeleteForm
from SanFranciscanos.db import get_mongo_db

bp = Blueprint('students', __name__, url_prefix='/students')


@bp.route('/')
def list_students():
    db = get_mongo_db()
    students = list(db.students.find())
    delete_form = DeleteForm()
    return render_template('students/list_students.html', students=students, delete_form=delete_form, title="Lista de Catequizados")


@bp.route('/create', methods=['GET', 'POST'])
def create_student():
    db = get_mongo_db()
    form = StudentForm()
    if form.validate_on_submit():
        data = {key: value for key, value in form.data.items() if key not in ('csrf_token', 'submit')}
        db.students.insert_one(data)
        flash('Catequizado registrado exitosamente.', 'success')
        return redirect(url_for('students.list_students'))
    return render_template('students/student_form.html', form=form, title="Nuevo Catequizado")


@bp.route('/edit/<id>', methods=['GET', 'POST'])
def edit_student(id):
    db = get_mongo_db()
    student = db.students.find_one({'_id': ObjectId(id)})

    if not student:
        flash('Catequizado no encontrado.', 'danger')
        return redirect(url_for('students.list_students'))

    form = StudentForm(data=student)

    if form.validate_on_submit():
        update_data = {key: value for key, value in form.data.items() if key not in ('csrf_token', 'submit')}
        db.students.update_one({'_id': ObjectId(id)}, {'$set': update_data})
        flash('Catequizado actualizado correctamente.', 'success')
        return redirect(url_for('students.list_students'))

    return render_template('students/student_form.html', form=form, student=student, title="Editar Catequizado")


@bp.route('/detail/<id>')
def view_student(id):
    db = get_mongo_db()
    student = db.students.find_one({'_id': ObjectId(id)})

    if not student:
        flash('Catequizado no encontrado.', 'danger')
        return redirect(url_for('students.list_students'))

    return render_template('students/detail_student.html', student=student, title="Detalle del Catequizado")


@bp.route('/delete/<id>', methods=['POST'])
def delete_student(id):
    db = get_mongo_db()
    result = db.students.delete_one({'_id': ObjectId(id)})
    if result.deleted_count:
        flash('Catequizado eliminado correctamente.', 'success')
    else:
        flash('No se encontró el catequizado para eliminar.', 'danger')
    return redirect(url_for('students.list_students'))
