from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from bson import ObjectId
from SanFranciscanos.forms import CursoForm, DeleteForm
import datetime

bp = Blueprint('Courses', __name__, url_prefix='/courses')

@bp.route('/')
def index():
    courses = list(current_app.mongo_db.courses.find())
    delete_form = DeleteForm()
    return render_template('courses/list_courses.html', courses=courses, delete_form=delete_form, title="Cursos")

@bp.route('/new', methods=['GET', 'POST'])
def create_course():
    form = CursoForm()
    if form.validate_on_submit():
        course = {
            'name': form.name.data,
            'idParroquia': form.idParroquia.data,
            'idCatequista': form.idCatequista.data,
            'idLevel': form.idLevel.data,
            'startDate': form.startDate.data,
            'endDate': form.endDate.data,
            'createdAt': datetime.datetime.utcnow(),
            'updatedAt': datetime.datetime.utcnow(),
            'state': 'Activo'
        }
        current_app.mongo_db.courses.insert_one(course)
        flash('Curso creado exitosamente.', 'success')
        return redirect(url_for('Courses.index'))
    return render_template('courses/course_form.html', form=form, title="Nuevo Curso")

@bp.route('/<id>')
def detail_course(id):
    course = current_app.mongo_db.courses.find_one({'_id': ObjectId(id)})
    if not course:
        flash('Curso no encontrado.', 'danger')
        return redirect(url_for('Courses.index'))
    return render_template('courses/detail_course.html', course=course, title="Detalle del Curso")

@bp.route('/edit/<id>', methods=['GET', 'POST'])
def edit_course(id):
    course = current_app.mongo_db.courses.find_one({'_id': ObjectId(id)})
    if not course:
        flash('Curso no encontrado.', 'danger')
        return redirect(url_for('Courses.index'))

    form = CursoForm(data=course)

    if form.validate_on_submit():
        updates = {
            'name': form.name.data,
            'idParroquia': form.idParroquia.data,
            'idCatequista': form.idCatequista.data,
            'idLevel': form.idLevel.data,
            'startDate': form.startDate.data,
            'endDate': form.endDate.data,
            'updatedAt': datetime.datetime.utcnow()
        }
        current_app.mongo_db.courses.update_one({'_id': ObjectId(id)}, {'$set': updates})
        flash('Curso actualizado exitosamente.', 'success')
        return redirect(url_for('Courses.index'))

    return render_template('courses/course_form.html', form=form, title="Editar Curso")

@bp.route('/delete/<id>', methods=['POST'])
def delete_course(id):
    current_app.mongo_db.courses.delete_one({'_id': ObjectId(id)})
    flash('Curso eliminado correctamente.', 'success')
    return redirect(url_for('Courses.index'))
