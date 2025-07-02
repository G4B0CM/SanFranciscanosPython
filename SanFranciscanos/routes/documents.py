from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from bson import ObjectId
from SanFranciscanos.forms import DocumentForm, DeleteForm
import datetime

bp = Blueprint('Documents', __name__, url_prefix='/documents')

@bp.route('/')
def index():
    documents = list(current_app.mongo_db.documents.find())
    delete_form = DeleteForm()
    return render_template('documents/list_documents.html', documents=documents, delete_form=delete_form, title="Documentos")

@bp.route('/new', methods=['GET', 'POST'])
def new():
    form = DocumentForm()
    if form.validate_on_submit():
        document = {
            'name': form.name.data,
            'type': form.type.data,
            'description': form.description.data,
            'createdAt': datetime.datetime.utcnow(),
            "category": form.category.data,
            'updatedAt': datetime.datetime.utcnow(),
            'state': 'Activo'
        }
        current_app.mongo_db.documents.insert_one(document)
        flash('Documento creado exitosamente.', 'success')
        return redirect(url_for('Documents.index'))
    return render_template('documents/document_form.html', form=form, title="Nuevo Documento")

@bp.route('/<id>')
def detail(id):
    document = current_app.mongo_db.documents.find_one({'_id': ObjectId(id)})
    if not document:
        flash('Documento no encontrado.', 'danger')
        return redirect(url_for('Documents.index'))
    return render_template('documents/detail_document.html', document=document, title="Detalle de Documento")

@bp.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    document = current_app.mongo_db.documents.find_one({'_id': ObjectId(id)})
    if not document:
        flash('Documento no encontrado.', 'danger')
        return redirect(url_for('Documents.index'))

    form = DocumentForm(data=document)

    if form.validate_on_submit():
        updates = {
            'name': form.name.data,
            'type': form.type.data,
            'description': form.description.data,
            "category": form.category.data,
            'updatedAt': datetime.datetime.utcnow()
        }
        current_app.mongo_db.documents.update_one({'_id': ObjectId(id)}, {'$set': updates})
        flash('Documento actualizado exitosamente.', 'success')
        return redirect(url_for('Documents.index'))

    return render_template('documents/document_form.html', form=form, title="Editar Documento")

@bp.route('/delete/<id>', methods=['POST'])
def delete(id):
    current_app.mongo_db.documents.delete_one({'_id': ObjectId(id)})
    flash('Documento eliminado correctamente.', 'success')
    return redirect(url_for('Documents.index'))
