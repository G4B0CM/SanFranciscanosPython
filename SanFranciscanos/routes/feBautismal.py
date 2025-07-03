from flask import Blueprint, render_template, request, redirect, url_for, flash
from bson.objectid import ObjectId
from datetime import datetime
from SanFranciscanos.db import get_mongo_db
from SanFranciscanos.forms import FeBautismalForm, DeleteForm

bp = Blueprint('feBautismal', __name__, url_prefix='/febautismal')

@bp.route('/')
def index():
    db = get_mongo_db()
    registros = list(db.feBautismal.find())
    delete_form = DeleteForm()
    return render_template('feBautismal/list_feBautismal.html', registros=registros, delete_form=delete_form, title="Registros Fe Bautismal")

@bp.route('/new', methods=['GET', 'POST'])
def create():
    db = get_mongo_db()
    form = FeBautismalForm()
    form.person_id.choices = [(str(p['_id']), f"{p.get('firstName', '')} {p.get('lastName', '')}") for p in db.students.find()]

    if form.validate_on_submit():
        data = {
            'person_id': form.person_id.data,
            'fecha_bautismo': form.fecha_bautismo.data,
            'iglesia': form.iglesia.data,
            'ciudad': form.ciudad.data,
            'notas': form.notas.data,
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow()
        }
        db.feBautismal.insert_one(data)
        flash('Registro de Fe Bautismal creado exitosamente.', 'success')
        return redirect(url_for('feBautismal.index'))

    return render_template('feBautismal/febautismal_form.html', form=form, title="Nuevo Registro de Fe Bautismal")

@bp.route('/<id>')
def detail(id):
    db = get_mongo_db()
    registro = db.feBautismal.find_one({'_id': ObjectId(id)})
    return render_template('feBautismal/detail_feBautismal.html', registro=registro, title="Detalle Fe Bautismal")

@bp.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    db = get_mongo_db()
    registro = db.feBautismal.find_one({'_id': ObjectId(id)})
    if not registro:
        flash("Registro no encontrado.", "danger")
        return redirect(url_for('feBautismal.index'))

    form = FeBautismalForm(**registro)
    form.person_id.choices = [(str(p['_id']), f"{p.get('firstName', '')} {p.get('lastName', '')}") for p in db.students.find()]
    form.person_id.data = registro.get('person_id')

    if form.validate_on_submit():
        updates = {
            'person_id': form.person_id.data,
            'fecha_bautismo': form.fecha_bautismo.data,
            'iglesia': form.iglesia.data,
            'ciudad': form.ciudad.data,
            'notas': form.notas.data,
            'updatedAt': datetime.utcnow()
        }
        db.feBautismal.update_one({'_id': ObjectId(id)}, {'$set': updates})
        flash("Registro actualizado exitosamente.", "success")
        return redirect(url_for('feBautismal.index'))

    return render_template('feBautismal/febautismal_form.html', form=form, title="Editar Registro")

@bp.route('/delete/<id>', methods=['POST'])
def delete(id):
    db = get_mongo_db()
    db.feBautismal.delete_one({'_id': ObjectId(id)})
    flash("Registro eliminado correctamente.", "success")
    return redirect(url_for('feBautismal.index'))
