from flask import Blueprint, render_template, request, redirect, url_for, flash
from bson.objectid import ObjectId
from SanFranciscanos.forms import InstitutionForm, DeleteForm
from SanFranciscanos.db import get_mongo_db  # ← IMPORTACIÓN CORRECTA

bp = Blueprint('institutions', __name__, url_prefix='/institutions')


@bp.route('/')
def list_institutions():
    db = get_mongo_db()
    tipo = request.args.get('tipo')
    query = {'tipo': tipo} if tipo else {}
    institutions = list(db['institutions'].find(query))
    delete_form = DeleteForm()
    return render_template('institutions/list_institutions.html',
                           institutions=institutions,
                           delete_form=delete_form,
                           title="Lista de Instituciones",
                           selected_tipo=tipo)


@bp.route('/create', methods=['GET', 'POST'])
def create_institution():
    db = get_mongo_db()
    form = InstitutionForm()
    if form.validate_on_submit():
        data = {k: v for k, v in form.data.items() if k not in ('csrf_token', 'submit')}
        db['institutions'].insert_one(data)
        flash(f"{data['tipo'].capitalize()} creada correctamente.", 'success')
        return redirect(url_for('institutions.list_institutions'))
    return render_template('institutions/institution_form.html', form=form, title="Nueva Institución")


@bp.route('/edit/<id>', methods=['GET', 'POST'])
def edit_institution(id):
    db = get_mongo_db()
    institution = db['institutions'].find_one({'_id': ObjectId(id)})

    if not institution:
        flash('Institución no encontrada.', 'danger')
        return redirect(url_for('institutions.list_institutions'))

    form = InstitutionForm(data=institution)
    if form.validate_on_submit():
        data = {k: v for k, v in form.data.items() if k not in ('csrf_token', 'submit')}
        db['institutions'].update_one({'_id': ObjectId(id)}, {'$set': data})
        flash(f"{data['tipo'].capitalize()} actualizada correctamente.", 'success')
        return redirect(url_for('institutions.list_institutions'))

    return render_template('institutions/institution_form.html', form=form, title="Editar Institución", institution=institution)


@bp.route('/detail/<id>')
def view_institution(id):
    db = get_mongo_db()
    institution = db['institutions'].find_one({'_id': ObjectId(id)})

    if not institution:
        flash('Institución no encontrada.', 'danger')
        return redirect(url_for('institutions.list_institutions'))

    return render_template('institutions/detail_institution.html', institution=institution, title="Detalle de Institución")


@bp.route('/delete/<id>', methods=['POST'])
def delete_institution(id):
    db = get_mongo_db()
    result = db['institutions'].delete_one({'_id': ObjectId(id)})
    if result.deleted_count:
        flash('Institución eliminada correctamente.', 'success')
    else:
        flash('No se encontró la institución.', 'danger')
    return redirect(url_for('institutions.list_institutions'))


@bp.route('/arquidiocesis')
def list_arquidiocesis():
    db = get_mongo_db()
    arquidiocesis = list(db['institutions'].find({'tipo': 'arquidiocesis'}))
    delete_form = DeleteForm()
    return render_template('institutions/list_arquidiocesis.html', institutions=arquidiocesis, delete_form=delete_form, title="Lista de Arquidiócesis")


@bp.route('/vicarias')
def list_vicarias():
    db = get_mongo_db()
    vicarias = list(db['institutions'].find({'tipo': 'vicaria'}))
    delete_form = DeleteForm()
    return render_template('institutions/list_vicarias.html', institutions=vicarias, delete_form=delete_form, title="Lista de Vicarías")


@bp.route('/parroquias')
def list_parroquias():
    db = get_mongo_db()
    parroquias = list(db['institutions'].find({'tipo': 'parroquia'}))
    delete_form = DeleteForm()
    return render_template('institutions/list_parroquias.html', institutions=parroquias, delete_form=delete_form, title="Lista de Parroquias")
