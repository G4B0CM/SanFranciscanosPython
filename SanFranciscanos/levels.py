# backend/levels.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, abort
from sqlalchemy import text, exc
from .forms import (
    LevelForm, CursoForm, 
    LevelRolSelectorForm, DeleteForm
)
import datetime

bp = Blueprint('Levels', __name__, url_prefix='/Levels')

def get_item_details(role):
    """
    Devuelve un diccionario centralizado para Nivel o Curso.
    """
    roles = {
        'Level': {
            'form': LevelForm,
            'sp_insert': 'sp_InsertLevel',
            'sp_update': 'sp_UpdateLevel',
            'sp_delete': 'sp_DeleteLevel',
            'view': 'v_InfoLevel',
            'list_headers': ['ID', 'Nombre', 'Número de Orden', 'Siguiente Nivel'],
            'detail_fields': {
                'ID': 'ID', 'Nombre': 'Nombre', 'Descripción': 'Descripción',
                'Número de Orden': 'Orden', 'Siguiente Nivel': 'Próximo Nivel',
                'Sacramento que Habilita': 'Sacramento Asociado'
            },
            'output_param': 'CreatedLevelID',
            'id_param': 'idLevel' # Nombre del param PK para los SPs
        },
        'Curso': {
            'form': CursoForm,
            'sp_insert': 'sp_InsertCurso',
            'sp_update': 'sp_UpdateCurso',
            'sp_delete': 'sp_DeleteCurso',
            'view': 'v_InfoCurso',
            'list_headers': ['ID', 'Nombre Nivel', 'Nombre Parroquia', 'Año del Período', 'Catequista Principal'],
            'detail_fields': {
                'ID': 'ID Curso', 'Nombre Nivel': 'Nivel', 'Nombre Parroquia': 'Parroquia',
                'Año del Período': 'Año', 'Fecha de Inicio': 'Inicio', 'Fecha de Fin': 'Fin',
                'Duración': 'Duración (Semanas)', 'Catequista Principal': 'Catequista',
                'Ayudante Asignado': 'Ayudante'
            },
            'output_param': 'CreatedCursoID',
            'id_param': 'idCurso'
        }
    }
    return roles.get(role)

def load_level_dynamic_choices(form, role, session):
    """Carga las opciones dinámicas para los formularios de Nivel y Curso."""
    if role == 'Level':
        form.idNextLevel.choices = [('', '-- Ninguno --')] + [(l.ID, l.Nombre) for l in session.execute(text("SELECT ID, Nombre FROM Nivel.v_InfoLevel ORDER BY [Número de Orden]")).mappings().all()]
        form.idEnabledSacrament.choices = [('', '-- Ninguno --')] + [(s.ID, s.Tipo) for s in session.execute(text("SELECT ID, Tipo FROM Sacraments.v_InfoSacrament ORDER BY Tipo")).mappings().all()]
    
    if role == 'Curso':
        form.idLevel.choices = [(l.ID, l.Nombre) for l in session.execute(text("SELECT ID, Nombre FROM Nivel.v_InfoLevel ORDER BY [Número de Orden]")).mappings().all()]
        form.idParroquia.choices = [(p['ID Institución'], p['Nombre Parroquia']) for p in session.execute(text("SELECT [ID Institución], [Nombre Parroquia] FROM Institutions.v_InfoParroquia ORDER BY [Nombre Parroquia]")).mappings().all()]
        form.idCatequista.choices = [(c.ID, c['Primer Nombre'] + ' ' + c['Primer Apellido']) for c in session.execute(text("SELECT ID, [Primer Nombre], [Primer Apellido] FROM Persons.v_InfoCatequista WHERE Estado = 1 ORDER BY [Primer Apellido]")).mappings().all()]
        form.idAyudante.choices = [('', '-- Ninguno --')] + [(a.ID, a['Primer Nombre'] + ' ' + a['Primer Apellido']) for a in session.execute(text("SELECT ID, [Primer Nombre], [Primer Apellido] FROM Persons.v_InfoAyudante ORDER BY [Primer Apellido]")).mappings().all()]

@bp.route('/', methods=['GET', 'POST'])
def index():
    form = LevelRolSelectorForm()
    if form.validate_on_submit():
        role = form.role.data
        return redirect(url_for('Levels.list_items', role=role))
    return render_template('Levels/select_role.html', form=form, title="Gestionar Niveles y Cursos")

@bp.route('/list/<role>')
def list_items(role):
    role_details = get_item_details(role)
    if not role_details: abort(404)
    SessionLocal = current_app.SessionLocal
    session = SessionLocal()
    try:
        results = session.execute(text(f"SELECT * FROM Nivel.{role_details['view']}")).mappings().all()
    finally:
        session.close()
    return render_template('Levels/list.html', items=results, headers=role_details['list_headers'], role=role, delete_form=DeleteForm(), title=f"Lista de {role}s")

@bp.route('/new/<role>', methods=['GET', 'POST'])
def new_item(role):
    role_details = get_item_details(role)
    if not role_details: abort(404)
    form = role_details['form']()
    SessionLocal = current_app.SessionLocal
    session = SessionLocal()
    try:
        load_level_dynamic_choices(form, role, session)
    finally:
        session.close()

    if form.validate_on_submit():
        params = {k: v for k, v in form.data.items() if k not in ['submit', 'csrf_token'] and v not in [None, '']}
        session = SessionLocal()
        try:
            output_param = role_details['output_param']
            placeholders = [f"@{k}=:{k}" for k in params.keys()]
            sql = f"""
                DECLARE @{output_param} INT;
                EXEC Nivel.{role_details['sp_insert']} {', '.join(placeholders)}, @{output_param}=@{output_param} OUTPUT;
                SELECT @{output_param};
            """
            created_id = session.execute(text(sql), params).scalar_one()
            session.commit()
            flash(f'{role} creado con ID: {created_id}.', 'success')
            return redirect(url_for('Levels.list_items', role=role))
        except exc.SQLAlchemyError as e:
            if session.is_active: session.rollback()
            flash(f"Error al crear {role}: {getattr(e, 'orig', e)}", 'danger')
        finally:
            session.close()
    return render_template('Levels/form.html', form=form, title=f'Nuevo {role}', role=role, action_url=url_for('Levels.new_item', role=role))

@bp.route('/edit/<role>/<int:item_id>', methods=['GET', 'POST'])
def edit_item(role, item_id):
    role_details = get_item_details(role)
    if not role_details: abort(404)
    form = role_details['form']()
    SessionLocal = current_app.SessionLocal
    session = SessionLocal()
    try:
        id_col = role_details['list_headers'][0]
        item_data = session.execute(text(f"SELECT * FROM Nivel.{role_details['view']} WHERE \"{id_col}\" = :id"), {"id": item_id}).mappings().fetchone()
        if not item_data:
            flash(f"{role} ID {item_id} no encontrado.", 'warning')
            return redirect(url_for('Levels.list_items', role=role))
        
        form = role_details['form'](data=item_data)
        load_level_dynamic_choices(form, role, session)

        if form.validate_on_submit():
            params = {k: v for k, v in form.data.items() if k not in ['submit', 'csrf_token']}
            params[role_details['id_param']] = item_id # Añadir el ID para el SP de update
            placeholders = [f"@{k}=:{k}" for k in params.keys()]
            sql = f"EXEC Nivel.{role_details['sp_update']} {', '.join(placeholders)}"
            session.execute(text(sql), params)
            session.commit()
            flash(f"{role} actualizado.", 'success')
            return redirect(url_for('Levels.list_items', role=role))
    finally:
        session.close()
    return render_template('Levels/form.html', form=form, title=f'Editar {role}', role=role, action_url=url_for('Levels.edit_item', role=role, item_id=item_id))

@bp.route('/delete/<role>/<int:item_id>', methods=['POST'])
def delete_item(role, item_id):
    role_details = get_item_details(role)
    if not role_details: abort(404)
    if not DeleteForm().validate_on_submit():
        flash('Intento de borrado no válido.', 'warning')
        return redirect(url_for('Levels.list_items', role=role))
    
    SessionLocal = current_app.SessionLocal
    session = SessionLocal()
    try:
        sql = text(f"EXEC Nivel.{role_details['sp_delete']} @{role_details['id_param']} = :id")
        session.execute(sql, {"id": item_id})
        session.commit()
        flash(f'{role} con ID {item_id} ha sido eliminado.', 'success')
    except exc.SQLAlchemyError as e:
        session.rollback()
        flash(f"Error al eliminar {role}: {getattr(e, 'orig', e)}", 'danger')
    finally:
        session.close()
    return redirect(url_for('Levels.list_items', role=role))

@bp.route('/<role>/<int:item_id>')
def detail_item(role, item_id):
    role_details = get_item_details(role)
    if not role_details: abort(404)
    SessionLocal = current_app.SessionLocal
    session = SessionLocal()
    try:
        id_col = role_details['list_headers'][0]
        item_data = session.execute(text(f"SELECT * FROM Nivel.{role_details['view']} WHERE \"{id_col}\" = :id"), {"id": item_id}).mappings().fetchone()
        if not item_data:
            return redirect(url_for('Levels.list_items', role=role))
        
        detail_items = [(label, item_data.get(col, 'N/A')) for col, label in role_details['detail_fields'].items()]
    finally:
        session.close()
    return render_template('Levels/detail.html', detail_items=detail_items, title=f"Detalle de {role}", role=role)