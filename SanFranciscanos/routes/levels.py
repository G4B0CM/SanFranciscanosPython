from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from bson import ObjectId
from SanFranciscanos.forms import LevelForm, DeleteForm
import datetime

bp = Blueprint('Levels', __name__, url_prefix='/levels')

@bp.route('/')
def index():
    levels = list(current_app.mongo_db.levels.find())
    delete_form = DeleteForm()
    return render_template('levels/list_levels.html', levels=levels, delete_form=delete_form, title="Niveles")

@bp.route('/new', methods=['GET', 'POST'])
def new():
    form = LevelForm()
    if form.validate_on_submit():
        level = {
            'name': form.name.data,
            'description': form.description.data,
            'createdAt': datetime.datetime.utcnow(),
            'updatedAt': datetime.datetime.utcnow(),
            'order': form.order.data,
            'state': 'Activo'
        }
        current_app.mongo_db.levels.insert_one(level)
        flash('Nivel creado exitosamente.', 'success')
        return redirect(url_for('Levels.index'))
    return render_template('levels/level_form.html', form=form, title="Nuevo Nivel")

@bp.route('/<id>')
def detail(id):
    level = current_app.mongo_db.levels.find_one({'_id': ObjectId(id)})
    if not level:
        flash('Nivel no encontrado.', 'danger')
        return redirect(url_for('Levels.index'))
    return render_template('levels/detail_level.html', level=level, title="Detalle del Nivel")

@bp.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    level = current_app.mongo_db.levels.find_one({'_id': ObjectId(id)})
    if not level:
        flash('Nivel no encontrado.', 'danger')
        return redirect(url_for('Levels.index'))

    form = LevelForm(data=level)

    if form.validate_on_submit():
        updates = {
            'name': form.name.data,
            'description': form.description.data,
            'order': form.order.data,
            'updatedAt': datetime.datetime.utcnow()
        }
        current_app.mongo_db.levels.update_one({'_id': ObjectId(id)}, {'$set': updates})
        flash('Nivel actualizado exitosamente.', 'success')
        return redirect(url_for('Levels.index'))

    return render_template('levels/level_form.html', form=form, title="Editar Nivel")

@bp.route('/delete/<id>', methods=['POST'])
def delete(id):
    current_app.mongo_db.levels.delete_one({'_id': ObjectId(id)})
    flash('Nivel eliminado correctamente.', 'success')
    return redirect(url_for('Levels.index'))
