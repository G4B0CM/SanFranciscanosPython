# backend/sacraments.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, abort
from sqlalchemy import text, exc
from .forms import (
    SacramentForm, CatequizadoSacramentoForm,
    SacramentRolSelectorForm, DeleteForm
)
import datetime

bp = Blueprint('Sacraments', __name__, url_prefix='/Sacraments')

def get_item_details(role):
    """Devuelve un diccionario centralizado para el módulo de Sacramentos."""
    roles = {
        'Sacrament': {
            'form': SacramentForm,
            'sp_insert': 'sp_InsertSacrament',
            'sp_update': 'sp_UpdateSacrament',
            'sp_delete': 'sp_DeleteSacrament',
            'view': 'v_InfoSacrament',
            'list_headers': ['ID', 'Tipo', 'Fecha de Celebración', 'Lugar (Parroquia)'],
            'detail_fields': {
                'ID': 'ID Evento', 'Tipo': 'Tipo', 'Fecha de Celebración': 'Fecha',
                'Lugar (Parroquia)': 'Lugar', 'Observaciones': 'Observaciones'
            },
            'output_param': 'CreatedSacramentID',
            'id_param': 'idSacrament'
        },
        'CatequizadoSacramento': {
            'form': CatequizadoSacramentoForm,
            'sp_insert': 'sp_InsertCatequizadoSacramento',
            'sp_update': 'sp_UpdateCatequizadoSacramento', # Actualiza el padrino
            'sp_delete': 'sp_DeleteCatequizadoSacramento',
            'view': 'v_InfoCatequizadoSacramento',
            'list_headers': ['Nombre Sacramento', 'Nombre Catequizado', 'Nombre Padrino'],
            'detail_fields': {
                'Nombre Sacramento': 'Sacramento', 'Fecha Celebración': 'Fecha',
                'Nombre Catequizado': 'Recibido por', 'Nombre Padrino': 'Apadrinado por'
            },
            # Esta entidad tiene clave primaria compuesta
            'id_param': ['idSacramento', 'idCatequizado'] 
        }
    }
    return roles.get(role)

def load_sacrament_dynamic_choices(form, role, session):
    """Carga las opciones dinámicas para los formularios."""
    if role == 'Sacrament':
        parroquias = session.execute(text("SELECT [ID Institución], [Nombre Parroquia] FROM Institutions.v_InfoParroquia ORDER BY [Nombre Parroquia]")).mappings().all()
        form.idInstitution.choices = [(p['ID Institución'], p['Nombre Parroquia']) for p in parroquias]
        form.idInstitution.choices.insert(0, ('', '-- Seleccione Parroquia --'))

    if role == 'CatequizadoSacramento':
        sacs = session.execute(text("SELECT ID, Tipo, [Fecha de Celebración] FROM Sacraments.v_InfoSacrament ORDER BY [Fecha de Celebración] DESC")).mappings().all()
        form.idSacramento.choices = [(s.ID, f"{s.Tipo} ({s['Fecha de Celebración'].strftime('%Y-%m-%d')})") for s in sacs]
        
        cats = session.execute(text("SELECT ID, [Primer Nombre], [Primer Apellido] FROM Persons.v_InfoCatequizado WHERE Estado = 1 ORDER BY [Primer Apellido]")).mappings().all()
        form.idCatequizado.choices = [(c.ID, f"{c['Primer Nombre']} {c['Primer Apellido']}") for c in cats]

        padrinos = session.execute(text("SELECT ID, [Primer Nombre], [Primer Apellido] FROM Persons.v_InfoPadrino ORDER BY [Primer Apellido]")).mappings().all()
        form.idPadrino.choices = [('', '-- Ninguno --')] + [(p.ID, f"{p['Primer Nombre']} {p['Primer Apellido']}") for p in padrinos]

@bp.route('/', methods=['GET', 'POST'])
def index():
    form = SacramentRolSelectorForm()
    if form.validate_on_submit():
        return redirect(url_for('Sacraments.list_items', role=form.role.data))
    return render_template('Sacraments/select_role.html', form=form, title="Gestionar Sacramentos")

@bp.route('/list/<role>')
def list_items(role):
    role_details = get_item_details(role)
    if not role_details: abort(404)
    SessionLocal = current_app.SessionLocal
    session = SessionLocal()
    try:
        results = session.execute(text(f"SELECT * FROM Sacraments.{role_details['view']}")).mappings().all()
    finally:
        session.close()
    return render_template('Sacraments/list.html', items=results, headers=role_details['list_headers'], role=role, delete_form=DeleteForm(), title=f"Lista de {role}s")

@bp.route('/new/<role>', methods=['GET', 'POST'])
def new_item(role):
    role_details = get_item_details(role)
    if not role_details: abort(404)
    form = role_details['form']()
    SessionLocal = current_app.SessionLocal
    session = SessionLocal()
    try:
        load_sacrament_dynamic_choices(form, role, session)
    finally:
        session.close()

    if form.validate_on_submit():
        params = {k: v for k, v in form.data.items() if k not in ['submit', 'csrf_token'] and v not in [None, '']}
        session = SessionLocal()
        try:
            placeholders = [f"@{k}=:{k}" for k in params.keys()]
            if 'output_param' in role_details:
                # Lógica para Sacrament, que devuelve un ID
                output_param = role_details['output_param']
                sql = f"""
                    DECLARE @{output_param} INT;
                    EXEC Sacraments.{role_details['sp_insert']} {', '.join(placeholders)}, @{output_param}=@{output_param} OUTPUT;
                    SELECT @{output_param};
                """
                created_id = session.execute(text(sql), params).scalar_one()
                flash(f'{role} creado con ID: {created_id}.', 'success')
            else:
                # Lógica para CatequizadoSacramento, que no devuelve ID
                sql = f"EXEC Sacraments.{role_details['sp_insert']} {', '.join(placeholders)}"
                session.execute(text(sql), params)
                flash(f'{role} asignado exitosamente.', 'success')
            
            session.commit()
            return redirect(url_for('Sacraments.list_items', role=role))
        except exc.SQLAlchemyError as e:
            if session.is_active: session.rollback()
            flash(f"Error al crear {role}: {getattr(e, 'orig', e)}", 'danger')
        finally:
            session.close()
    return render_template('Sacraments/form.html', form=form, title=f'Nuevo {role}', role=role, action_url=url_for('Sacraments.new_item', role=role))

# Para la edición de una asignación, necesitamos una ruta especial con la clave compuesta
@bp.route('/edit/CatequizadoSacramento/<int:sacrament_id>/<int:catequizado_id>', methods=['GET', 'POST'])
def edit_assignment(sacrament_id, catequizado_id):
    role = 'CatequizadoSacramento'
    role_details = get_item_details(role)
    form = role_details['form']()
    SessionLocal = current_app.SessionLocal
    session = SessionLocal()
    try:
        # Cargamos los datos actuales para pre-llenar el formulario
        item_data = session.execute(text(f"SELECT * FROM Sacraments.{role_details['view']} WHERE [ID Sacramento] = :sid AND [ID Catequizado] = :cid"), {"sid": sacrament_id, "cid": catequizado_id}).mappings().fetchone()
        if not item_data:
            flash("Asignación no encontrada.", 'warning')
            return redirect(url_for('Sacraments.list_items', role=role))
        
        form = role_details['form'](data=item_data)
        # Deshabilitamos los campos de la PK para que no se puedan cambiar
        form.idSacramento.render_kw = {'disabled': 'disabled'}
        form.idCatequizado.render_kw = {'disabled': 'disabled'}
        load_sacrament_dynamic_choices(form, role, session)

        if form.validate_on_submit():
            # Solo actualizamos el padrino, ya que es el único campo editable
            params = {'idSacramento': sacrament_id, 'idCatequizado': catequizado_id, 'idPadrino': form.idPadrino.data or None}
            sql = text(f"EXEC Sacraments.{role_details['sp_update']} @idSacramento=:idSacramento, @idCatequizado=:idCatequizado, @idPadrino=:idPadrino")
            session.execute(sql, params)
            session.commit()
            flash('Padrino de la asignación actualizado.', 'success')
            return redirect(url_for('Sacraments.list_items', role=role))
    finally:
        session.close()
    
    return render_template('Sacraments/form.html', form=form, title='Editar Asignación', role=role, action_url=url_for('Sacraments.edit_assignment', sacrament_id=sacrament_id, catequizado_id=catequizado_id))


# La ruta de edición para Sacrament sigue el patrón normal
@bp.route('/edit/<role>/<int:item_id>', methods=['GET', 'POST'])
def edit_item(role, item_id):
    if role == 'CatequizadoSacramento':
        # Esta ruta no maneja asignaciones, las redirigimos a la suya
        return redirect(url_for('Sacraments.list_items', role=role))

    role_details = get_item_details(role)
    if not role_details: abort(404)
    
    # ... (El resto del código es idéntico al de levels.py para editar un 'Sacrament')
    # Por brevedad, se omite, pero es una copia del `edit_item` de levels.py.
    # El código a continuación es el que debe ir aquí:
    form = role_details['form']()
    SessionLocal = current_app.SessionLocal
    session = SessionLocal()
    try:
        id_col = role_details['list_headers'][0]
        item_data = session.execute(text(f"SELECT * FROM Sacraments.{role_details['view']} WHERE \"{id_col}\" = :id"), {"id": item_id}).mappings().fetchone()
        if not item_data:
            flash(f"{role} ID {item_id} no encontrado.", 'warning')
            return redirect(url_for('Sacraments.list_items', role=role))
        
        form = role_details['form'](data=item_data)
        load_sacrament_dynamic_choices(form, role, session)

        if form.validate_on_submit():
            params = {k: v for k, v in form.data.items() if k not in ['submit', 'csrf_token']}
            params[role_details['id_param']] = item_id
            placeholders = [f"@{k}=:{k}" for k in params.keys()]
            sql = f"EXEC Sacraments.{role_details['sp_update']} {', '.join(placeholders)}"
            session.execute(text(sql), params)
            session.commit()
            flash(f"{role} actualizado.", 'success')
            return redirect(url_for('Sacraments.list_items', role=role))
    finally:
        session.close()
    return render_template('Sacraments/form.html', form=form, title=f'Editar {role}', role=role, action_url=url_for('Sacraments.edit_item', role=role, item_id=item_id))


@bp.route('/delete/<role>', methods=['POST'])
def delete_item(role):
    role_details = get_item_details(role)
    if not role_details: abort(404)
    if not DeleteForm().validate_on_submit():
        return redirect(url_for('Sacraments.list_items', role=role))
    
    SessionLocal = current_app.SessionLocal
    session = SessionLocal()
    try:
        if isinstance(role_details['id_param'], list):
            # Caso para clave compuesta (CatequizadoSacramento)
            params = {
                'idSacramento': request.form.get('idSacramento'),
                'idCatequizado': request.form.get('idCatequizado')
            }
            sql = text(f"EXEC Sacraments.{role_details['sp_delete']} @idSacramento=:idSacramento, @idCatequizado=:idCatequizado")
            session.execute(sql, params)
        else:
            # Caso para clave simple (Sacrament)
            item_id = request.form.get('item_id')
            sql = text(f"EXEC Sacraments.{role_details['sp_delete']} @{role_details['id_param']} = :id")
            session.execute(sql, {"id": item_id})
        
        session.commit()
        flash(f'{role} ha sido eliminado.', 'success')
    except exc.SQLAlchemyError as e:
        session.rollback()
        flash(f"Error al eliminar {role}: {getattr(e, 'orig', e)}", 'danger')
    finally:
        session.close()
    return redirect(url_for('Sacraments.list_items', role=role))