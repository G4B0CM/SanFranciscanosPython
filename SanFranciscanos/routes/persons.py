from flask import Blueprint, render_template, request, redirect, url_for, flash
from bson.objectid import ObjectId
from datetime import datetime
from SanFranciscanos.forms import PersonForm, DeleteForm
from SanFranciscanos.db import get_mongo_db

bp = Blueprint('persons', __name__, url_prefix='/persons')

@bp.route('/')
def index():
    db = get_mongo_db()
    persons = list(db['persons'].find())
    delete_form = DeleteForm()
    return render_template('persons/list_persons.html', persons=persons, delete_form=delete_form, title="Personas")

@bp.route('/new', methods=['GET', 'POST'])
def new():
    db = get_mongo_db()
    form = PersonForm()
    if form.validate_on_submit():
        person = {
            'name': form.name.data,
            'surname': form.surname.data,
            'document': form.document.data,
            'birthdate': datetime.combine(form.birthdate.data, datetime.min.time()),
            'role': form.role.data,
            'state': 'Activo',
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow()
        }
        result = db['persons'].insert_one(person)
        flash('Persona creada exitosamente.', 'success')
        
        # Si es un Catequizando, redirige a crear certificado
        if form.role.data == 'Catequizando':
            return redirect(url_for('certificates.create_certificate', catequizado_id=str(result.inserted_id)))
        return redirect(url_for('persons.index'))
    return render_template('persons/person_form.html', form=form, title="Nueva Persona")

@bp.route('/<id>')
def detail(id):
    db = get_mongo_db()
    person = db['persons'].find_one({'_id': ObjectId(id)})
    if not person:
        flash('Persona no encontrada.', 'danger')
        return redirect(url_for('persons.index'))
    return render_template('persons/detail_person.html', person=person, title="Detalle de Persona")

@bp.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    db = get_mongo_db()
    person = db['persons'].find_one({'_id': ObjectId(id)})
    if not person:
        flash('Persona no encontrada.', 'danger')
        return redirect(url_for('persons.index'))

    form = PersonForm(data=person)

    if form.validate_on_submit():
        updates = {
            'name': form.name.data,
            'surname': form.surname.data,
            'document': form.document.data,
            'birthdate': datetime.combine(form.birthdate.data, datetime.min.time()),
            'role': form.role.data,
            'updatedAt': datetime.utcnow()
        }
        db['persons'].update_one({'_id': ObjectId(id)}, {'$set': updates})
        flash('Persona actualizada exitosamente.', 'success')
        return redirect(url_for('persons.index'))

    return render_template('persons/person_form.html', form=form, title="Editar Persona")

@bp.route('/delete/<id>', methods=['POST'])
def delete(id):
    db = get_mongo_db()
    db['persons'].delete_one({'_id': ObjectId(id)})
    flash('Persona eliminada correctamente.', 'success')
    return redirect(url_for('persons.index'))

@bp.route('/role/<role>')
def list_by_role(role):
    db = get_mongo_db()
    persons = list(db['persons'].find({'role': role}))
    delete_form = DeleteForm()
    return render_template('persons/list_persons.html', persons=persons, delete_form=delete_form, title=f"Personas: {role}")

@bp.route('/nuevo-catequizado', methods=['GET', 'POST'])
def nuevo_catequizado():
    db = get_mongo_db()
    form = PersonForm()

    # Eliminar el campo "role" del formulario para no mostrarlo al usuario
    del form.role

    if form.validate_on_submit():
        catequizado = {
            "name": form.name.data,
            "surname": form.surname.data,
            "document": form.document.data,
            "birthdate": datetime.combine(form.birthdate.data, datetime.min.time()),
            "role": "Catequizado",  
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        db.persons.insert_one(catequizado)
        flash("Catequizado creado correctamente.", "success")
        return redirect(url_for('persons.list_by_role', role='Catequizado'))

    return render_template('persons/simple_form.html', form=form, title="Nuevo Catequizado")
