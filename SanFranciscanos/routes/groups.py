from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from bson import ObjectId
from SanFranciscanos.forms import GruposForm, DeleteForm
from datetime import datetime

bp = Blueprint('Groups', __name__, url_prefix='/groups')

@bp.route('/')
def index():
    grupos = current_app.mongo_db.groups.find()
    cursos = {str(curso['_id']): curso['name'] for curso in current_app.mongo_db.courses.find()}
    catequizados = {str(person['_id']): person['c_firstName'] + ' ' + person['c_lastName']
                    for person in current_app.mongo_db.persons.find()}
    return render_template('groups/list_groups.html', grupos=grupos, cursos=cursos, catequizados=catequizados, delete_form=DeleteForm())

@bp.route('/new', methods=['GET', 'POST'])
def new():
    form = GruposForm()
    if form.validate_on_submit():
        nuevo_grupo = {
            'idCatequizado': ObjectId(form.idCatequizado.data),
            'idCurso': ObjectId(form.idCurso.data),
            'fechaInscripcion': form.fechaInscripcion.data,
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow()
        }
        current_app.mongo_db.groups.insert_one(nuevo_grupo)
        flash('Grupo inscrito correctamente.')
        return redirect(url_for('Groups.index'))

    # Cargar opciones para los selects
    form.idCatequizado.choices = [(str(p['_id']), f"{p['c_firstName']} {p['c_lastName']}") for p in current_app.mongo_db.persons.find()]
    form.idCurso.choices = [(str(c['_id']), c['name']) for c in current_app.mongo_db.courses.find()]

    return render_template('groups/group_form.html', form=form, title="Nuevo Grupo")

@bp.route('/<id>')
def detail(id):
    grupo = current_app.mongo_db.groups.find_one({'_id': ObjectId(id)})
    curso = current_app.mongo_db.courses.find_one({'_id': grupo['idCurso']})
    catequizado = current_app.mongo_db.persons.find_one({'_id': grupo['idCatequizado']})
    return render_template('groups/detail_group.html', grupo=grupo, curso=curso, catequizado=catequizado)

@bp.route('/<id>/edit', methods=['GET', 'POST'])
def edit(id):
    grupo = current_app.mongo_db.groups.find_one({'_id': ObjectId(id)})
    form = GruposForm(data={
        'idCatequizado': str(grupo['idCatequizado']),
        'idCurso': str(grupo['idCurso']),
        'fechaInscripcion': grupo['fechaInscripcion'].strftime('%Y-%m-%d')
    })

    # Cargar opciones para los selects
    form.idCatequizado.choices = [(str(p['_id']), f"{p['c_firstName']} {p['c_lastName']}") for p in current_app.mongo_db.persons.find()]
    form.idCurso.choices = [(str(c['_id']), c['name']) for c in current_app.mongo_db.courses.find()]

    if form.validate_on_submit():
        update_data = {
            'idCatequizado': ObjectId(form.idCatequizado.data),
            'idCurso': ObjectId(form.idCurso.data),
            'fechaInscripcion': form.fechaInscripcion.data,
            'updatedAt': datetime.utcnow()
        }
        current_app.mongo_db.groups.update_one({'_id': ObjectId(id)}, {'$set': update_data})
        flash('Grupo actualizado correctamente.')
        return redirect(url_for('Groups.index'))

    return render_template('groups/group_form.html', form=form, title="Editar Grupo")

@bp.route('/<id>/delete', methods=['POST'])
def delete(id):
    current_app.mongo_db.groups.delete_one({'_id': ObjectId(id)})
    flash('Inscripción eliminada correctamente.')
    return redirect(url_for('Groups.index'))
