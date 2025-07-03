from flask import Blueprint, render_template, request, redirect, url_for, flash
from bson import ObjectId
from SanFranciscanos.forms import CursoForm, DeleteForm
from SanFranciscanos.db import get_mongo_db
import datetime

bp = Blueprint('courses', __name__, url_prefix='/courses')


@bp.route('/')
def index():
    db = get_mongo_db()
    courses = list(db.courses.find())

    for course in courses:
        parroquia = db.institutions.find_one({'_id': course.get('idParroquia')})
        course['parroquia_name'] = parroquia['name'] if parroquia else 'Desconocido'

        catequista = db.persons.find_one({'_id': course.get('idCatequista')})
        if catequista:
            nombres = f"{catequista.get('c_firstName') or catequista.get('firstName', '')} {catequista.get('c_lastName') or catequista.get('lastName', '')}".strip()
            course['catequista_name'] = nombres
        else:
            course['catequista_name'] = 'Desconocido'

        nivel = db.levels.find_one({'_id': course.get('idLevel')})
        course['level_name'] = nivel['name'] if nivel else 'Desconocido'

    delete_form = DeleteForm()
    return render_template('courses/list_courses.html', courses=courses, delete_form=delete_form, title="Cursos")


@bp.route('/new', methods=['GET', 'POST'])
def create_course():
    db = get_mongo_db()
    form = CursoForm()

    form.idParroquia.choices = [(str(i['_id']), i['name']) for i in db.institutions.find()]
    form.idCatequista.choices = [(str(p['_id']), f"{p.get('c_firstName', '')} {p.get('c_lastName', '')}") for p in db.persons.find({'role': 'Catequista'})]
    form.idLevel.choices = [(str(l['_id']), l['name']) for l in db.levels.find()]

    if form.validate_on_submit():
        try:
            id_parroquia = ObjectId(form.idParroquia.data)
            id_catequista = ObjectId(form.idCatequista.data)
            id_level = ObjectId(form.idLevel.data)
        except Exception:
            flash("Uno de los ID seleccionados no es válido.", "danger")
            return redirect(url_for('courses.create_course'))

        if not all([
            db.institutions.find_one({'_id': id_parroquia}),
            db.persons.find_one({'_id': id_catequista}),
            db.levels.find_one({'_id': id_level})
        ]):
            flash("Una de las referencias seleccionadas no existe.", "danger")
            return redirect(url_for('courses.create_course'))

        course = {
            'name': form.name.data,
            'idParroquia': id_parroquia,
            'idCatequista': id_catequista,
            'idLevel': id_level,
            'startDate': form.startDate.data,
            'endDate': form.endDate.data,
            'createdAt': datetime.datetime.utcnow(),
            'updatedAt': datetime.datetime.utcnow(),
            'state': 'Activo'
        }

        db.courses.insert_one(course)
        flash('Curso creado exitosamente.', 'success')
        return redirect(url_for('courses.index'))

    return render_template('courses/course_form.html', form=form, title="Nuevo Curso")


@bp.route('/<id>')
def detail_course(id):
    db = get_mongo_db()
    try:
        course = db.courses.find_one({'_id': ObjectId(id)})
    except Exception:
        flash("ID de curso inválido.", "danger")
        return redirect(url_for('courses.index'))

    if not course:
        flash('Curso no encontrado.', 'danger')
        return redirect(url_for('courses.index'))

    catequista = db.persons.find_one({'_id': course.get('idCatequista')})
    parroquia = db.institutions.find_one({'_id': course.get('idParroquia')})
    level = db.levels.find_one({'_id': course.get('idLevel')})

    return render_template('courses/detail_course.html', course=course, catequista=catequista, parroquia=parroquia, level=level, title="Detalle del Curso")


@bp.route('/edit/<id>', methods=['GET', 'POST'])
def edit_course(id):
    db = get_mongo_db()
    try:
        course = db.courses.find_one({'_id': ObjectId(id)})
    except Exception:
        flash("ID de curso inválido.", "danger")
        return redirect(url_for('courses.index'))

    if not course:
        flash('Curso no encontrado.', 'danger')
        return redirect(url_for('courses.index'))

    form = CursoForm(
        name=course['name'],
        idParroquia=str(course['idParroquia']),
        idCatequista=str(course['idCatequista']),
        idLevel=str(course['idLevel']),
        startDate=course['startDate'],
        endDate=course['endDate']
    )

    form.idParroquia.choices = [(str(i['_id']), i['name']) for i in db.institutions.find()]
    form.idCatequista.choices = [(str(p['_id']), f"{p.get('c_firstName', '')} {p.get('c_lastName', '')}") for p in db.persons.find({'role': 'Catequista'})]
    form.idLevel.choices = [(str(l['_id']), l['name']) for l in db.levels.find()]

    if form.validate_on_submit():
        try:
            id_parroquia = ObjectId(form.idParroquia.data)
            id_catequista = ObjectId(form.idCatequista.data)
            id_level = ObjectId(form.idLevel.data)
        except Exception:
            flash("ID inválido en la edición.", "danger")
            return redirect(url_for('courses.edit_course', id=id))

        updates = {
            'name': form.name.data,
            'idParroquia': id_parroquia,
            'idCatequista': id_catequista,
            'idLevel': id_level,
            'startDate': form.startDate.data,
            'endDate': form.endDate.data,
            'updatedAt': datetime.datetime.utcnow()
        }

        db.courses.update_one({'_id': ObjectId(id)}, {'$set': updates})
        flash('Curso actualizado exitosamente.', 'success')
        return redirect(url_for('courses.index'))

    return render_template('courses/course_form.html', form=form, title="Editar Curso")


@bp.route('/delete/<id>', methods=['POST'])
def delete_course(id):
    db = get_mongo_db()
    try:
        db.courses.delete_one({'_id': ObjectId(id)})
        flash('Curso eliminado correctamente.', 'success')
    except Exception:
        flash('No se pudo eliminar el curso. ID inválido.', 'danger')
    return redirect(url_for('courses.index'))
