from flask import Blueprint, render_template, request, redirect, url_for, flash
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime
from SanFranciscanos.forms import GruposForm, DeleteForm
from SanFranciscanos.db import get_mongo_db

bp = Blueprint('groups', __name__, url_prefix='/groups')


@bp.route('/')
def index():
    db = get_mongo_db()
    grupos = list(db.groups.find())
    cursos = {str(curso['_id']): curso['name'] for curso in db.courses.find()}
    catequizados = {str(person['_id']): person['c_firstName'] + ' ' + person['c_lastName'] for person in db.persons.find()}
    delete_form = DeleteForm()
    return render_template('groups/list_groups.html', grupos=grupos, cursos=cursos,
                           catequizados=catequizados, delete_form=delete_form, title="Grupos")


@bp.route('/new', methods=['GET', 'POST'])
def new():
    db = get_mongo_db()
    form = GruposForm()
    form.idCatequizado.choices = [(str(p['_id']), f"{p['c_firstName']} {p['c_lastName']}") for p in db.persons.find()]
    form.idCurso.choices = [(str(c['_id']), c['name']) for c in db.courses.find()]

    if form.validate_on_submit():
        nuevo_grupo = {
            'idCatequizado': ObjectId(form.idCatequizado.data),
            'idCurso': ObjectId(form.idCurso.data),
            'fechaInscripcion': form.fechaInscripcion.data,
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow()
        }
        db.groups.insert_one(nuevo_grupo)
        flash('Inscripción creada exitosamente.', 'success')
        return redirect(url_for('groups.index'))

    return render_template('groups/group_form.html', form=form, title="Nuevo Grupo")


@bp.route('/<id>')
def detail(id):
    db = get_mongo_db()
    try:
        grupo = db.groups.find_one({'_id': ObjectId(id)})
    except InvalidId:
        flash("ID inválido.", "danger")
        return redirect(url_for('groups.index'))

    if not grupo:
        flash("Grupo no encontrado.", "danger")
        return redirect(url_for('groups.index'))

    curso = db.courses.find_one({'_id': grupo['idCurso']})
    catequizado = db.persons.find_one({'_id': grupo['idCatequizado']})

    return render_template('groups/detail_group.html', grupo=grupo, curso=curso,
                           catequizado=catequizado, title="Detalle de Grupo")


@bp.route('/<id>/edit', methods=['GET', 'POST'])
def edit(id):
    db = get_mongo_db()
    try:
        grupo = db.groups.find_one({'_id': ObjectId(id)})
    except InvalidId:
        flash("ID inválido.", "danger")
        return redirect(url_for('groups.index'))

    if not grupo:
        flash("Grupo no encontrado.", "danger")
        return redirect(url_for('groups.index'))

    form = GruposForm()
    form.idCatequizado.choices = [(str(p['_id']), f"{p['c_firstName']} {p['c_lastName']}") for p in db.persons.find()]
    form.idCurso.choices = [(str(c['_id']), c['name']) for c in db.courses.find()]

    if request.method == 'GET':
        form.idCatequizado.data = str(grupo['idCatequizado'])
        form.idCurso.data = str(grupo['idCurso'])
        form.fechaInscripcion.data = grupo['fechaInscripcion']

    if form.validate_on_submit():
        update_data = {
            'idCatequizado': ObjectId(form.idCatequizado.data),
            'idCurso': ObjectId(form.idCurso.data),
            'fechaInscripcion': form.fechaInscripcion.data,
            'updatedAt': datetime.utcnow()
        }
        db.groups.update_one({'_id': ObjectId(id)}, {'$set': update_data})
        flash('Grupo actualizado exitosamente.', 'success')
        return redirect(url_for('groups.index'))

    return render_template('groups/group_form.html', form=form, title="Editar Grupo")


@bp.route('/<id>/delete', methods=['POST'])
def delete(id):
    db = get_mongo_db()
    try:
        db.groups.delete_one({'_id': ObjectId(id)})
        flash('Inscripción eliminada correctamente.', 'success')
    except InvalidId:
        flash("ID inválido.", "danger")

    return redirect(url_for('groups.index'))
