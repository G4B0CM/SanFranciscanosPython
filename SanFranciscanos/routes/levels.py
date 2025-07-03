from flask import Blueprint, render_template, request, redirect, url_for, flash
from bson import ObjectId
from SanFranciscanos.forms import LevelForm, DeleteForm
from datetime import datetime
from SanFranciscanos.db import get_mongo_db

bp = Blueprint('levels', __name__, url_prefix='/levels')


@bp.route('/')
def index():
    db = get_mongo_db()
    levels = list(db['levels'].find())
    delete_form = DeleteForm()
    return render_template('levels/list_levels.html', levels=levels, delete_form=delete_form, title="Niveles")


@bp.route('/new', methods=['GET', 'POST'])
def new():
    db = get_mongo_db()
    form = LevelForm()
    if form.validate_on_submit():
        level = {
            'name': form.name.data,
            'description': form.description.data,
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow(),
            'order': form.order.data,
            'state': 'Activo'
        }
        db['levels'].insert_one(level)
        flash('Nivel creado exitosamente.', 'success')
        return redirect(url_for('levels.index'))
    return render_template('levels/level_form.html', form=form, title="Nuevo Nivel")


@bp.route('/<id>')
def detail(id):
    db = get_mongo_db()
    level = db['levels'].find_one({'_id': ObjectId(id)})
    if not level:
        flash('Nivel no encontrado.', 'danger')
        return redirect(url_for('levels.index'))
    return render_template('levels/detail_level.html', level=level, title="Detalle del Nivel")


@bp.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    db = get_mongo_db()
    level = db['levels'].find_one({'_id': ObjectId(id)})
    if not level:
        flash('Nivel no encontrado.', 'danger')
        return redirect(url_for('levels.index'))

    form = LevelForm(data=level)
    if form.validate_on_submit():
        updates = {
            'name': form.name.data,
            'description': form.description.data,
            'order': form.order.data,
            'updatedAt': datetime.utcnow()
        }
        db['levels'].update_one({'_id': ObjectId(id)}, {'$set': updates})
        flash('Nivel actualizado exitosamente.', 'success')
        return redirect(url_for('levels.index'))

    return render_template('levels/level_form.html', form=form, title="Editar Nivel")


@bp.route('/delete/<id>', methods=['POST'])
def delete(id):
    db = get_mongo_db()
    db['levels'].delete_one({'_id': ObjectId(id)})
    flash('Nivel eliminado correctamente.', 'success')
    return redirect(url_for('levels.index'))
