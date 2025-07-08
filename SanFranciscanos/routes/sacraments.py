from flask import Blueprint, render_template, request, redirect, url_for, flash
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime
from SanFranciscanos.forms import SacramentForm, DeleteForm
from SanFranciscanos.db import get_mongo_db

bp = Blueprint('sacraments', __name__, url_prefix='/sacraments')


@bp.route('/')
def index():
    db = get_mongo_db()
    sacraments = list(db.sacraments.find())
    delete_form = DeleteForm()
    return render_template('sacraments/list_sacraments.html',
                           sacraments=sacraments,
                           delete_form=delete_form,
                           title="Lista de Sacramentos")


@bp.route('/new', methods=['GET', 'POST'])
def new():
    db = get_mongo_db()
    form = SacramentForm()
    if form.validate_on_submit():
        sacrament = {
            'name': form.name.data,
            'description': form.description.data,
            'required': form.required.data,
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow(),
            'state': 'Activo'
        }
        db.sacraments.insert_one(sacrament)
        flash("Sacramento creado exitosamente.", 'success')
        return redirect(url_for('sacraments.index'))
    return render_template('sacraments/sacrament_form.html', form=form, title="Nuevo Sacramento")


@bp.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    db = get_mongo_db()
    try:
        sacrament = db.sacraments.find_one({'_id': ObjectId(id)})
    except Exception:
        flash("ID inválido.", 'danger')
        return redirect(url_for('sacraments.index'))

    if not sacrament:
        flash("Sacramento no encontrado.", 'warning')
        return redirect(url_for('sacraments.index'))

    form = SacramentForm(data=sacrament)
    if form.validate_on_submit():
        updates = {
            'name': form.name.data,
            'description': form.description.data,
            'required': form.required.data,
            'updatedAt': datetime.utcnow()
        }
        db.sacraments.update_one({'_id': ObjectId(id)}, {'$set': updates})
        flash("Sacramento actualizado exitosamente.", 'success')
        return redirect(url_for('sacraments.index'))

    return render_template('sacraments/sacrament_form.html', form=form, title="Editar Sacramento")


@bp.route('/delete/<id>', methods=['POST'])
def delete(id):
    db = get_mongo_db()
    try:
        db.sacraments.delete_one({'_id': ObjectId(id)})
        flash("Sacramento eliminado correctamente.", 'success')
    except Exception:
        flash("No se pudo eliminar el sacramento (ID inválido).", 'danger')
    return redirect(url_for('sacraments.index'))


@bp.route('/<id>')
def detail(id):
    db = get_mongo_db()
    try:
        sacrament = db.sacraments.find_one({'_id': ObjectId(id)})
    except Exception:
        flash("ID inválido.", 'danger')
        return redirect(url_for('sacraments.index'))

    if not sacrament:
        flash("Sacramento no encontrado.", 'warning')
        return redirect(url_for('sacraments.index'))

    return render_template('sacraments/detail_sacrament.html',
                           sacrament=sacrament,
                           title="Detalle del Sacramento")
