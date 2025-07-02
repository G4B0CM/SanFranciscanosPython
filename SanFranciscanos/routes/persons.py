from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from bson import ObjectId
from SanFranciscanos.forms import CatequistaForm, AyudanteForm, EclesiasticoForm, PadrinoForm, PadreMadreForm, RolSelectorForm, DeleteForm
import datetime

bp = Blueprint('Persons', __name__, url_prefix='/persons')

def get_form_and_template(role):
    if role == 'Catequista':
        return CatequistaForm(), 'catequista_form.html'
    elif role == 'Ayudante':
        return AyudanteForm(), 'ayudante_form.html'
    elif role == 'Eclesiastico':
        return EclesiasticoForm(), 'eclesiastico_form.html'
    elif role == 'Padrino':
        return PadrinoForm(), 'padrino_form.html'
    elif role == 'PadreMadre':
        return PadreMadreForm(), 'padremadre_form.html'
    return None, None

@bp.route('/', methods=['GET', 'POST'])
def index():
    form = RolSelectorForm()
    if form.validate_on_submit():
        role = form.role.data
        return redirect(url_for('Persons.new_person', role=role))
    return render_template('Persons/select_role.html', form=form, title="Seleccionar Rol")

@bp.route('/new/<role>', methods=['GET', 'POST'])
def new_person(role):
    form, template = get_form_and_template(role)
    if not form:
        flash('Rol no reconocido.', 'danger')
        return redirect(url_for('Persons.index'))

    if form.validate_on_submit():
        person = {key: value for key, value in form.data.items() if key != 'submit'}
        person.update({
            'role': role,
            'createdAt': datetime.datetime.utcnow(),
            'updatedAt': datetime.datetime.utcnow(),
            'state': 'Activo'
        })
        current_app.mongo_db.persons.insert_one(person)
        flash(f'{role} creado exitosamente.', 'success')
        return redirect(url_for('Persons.index'))

    return render_template(f'Persons/{template}', form=form, title=f'Nuevo {role}')

@bp.route('/list/<role>')
def list_persons(role):
    persons = list(current_app.mongo_db.persons.find({'role': role}))
    delete_form = DeleteForm()
    return render_template(f'Persons/list_{role.lower()}.html', persons=persons, role=role, delete_form=delete_form, title=f"Lista de {role}s")

@bp.route('/delete/<role>/<id>', methods=['POST'])
def delete_person(role, id):
    current_app.mongo_db.persons.delete_one({'_id': ObjectId(id)})
    flash(f'{role} eliminado correctamente.', 'success')
    return redirect(url_for('Persons.list_persons', role=role))

@bp.route('/edit/<role>/<id>', methods=['GET', 'POST'])
def edit_person(role, id):
    form, template = get_form_and_template(role)
    if not form:
        flash('Rol no reconocido.', 'danger')
        return redirect(url_for('Persons.index'))

    person = current_app.mongo_db.persons.find_one({'_id': ObjectId(id)})
    if not person:
        flash(f"{role} no encontrado.", 'warning')
        return redirect(url_for('Persons.list_persons', role=role))

    if request.method == 'GET':
        for field in form:
            if field.name in person:
                field.data = person[field.name]

    if form.validate_on_submit():
        updates = {key: value for key, value in form.data.items() if key != 'submit'}
        updates['updatedAt'] = datetime.datetime.utcnow()
        current_app.mongo_db.persons.update_one({'_id': ObjectId(id)}, {'$set': updates})
        flash(f"{role} actualizado exitosamente.", 'success')
        return redirect(url_for('Persons.list_persons', role=role))

    return render_template(f'Persons/{template}', form=form, title=f'Editar {role}')

@bp.route('/<role>/<id>')
def detail_person(role, id):
    person = current_app.mongo_db.persons.find_one({'_id': ObjectId(id)})
    if not person:
        flash(f"{role} no encontrado.", 'warning')
        return redirect(url_for('Persons.list_persons', role=role))
    return render_template(f'Persons/detail_{role.lower()}.html', person=person, role=role, title=f"Detalle de {role}")
