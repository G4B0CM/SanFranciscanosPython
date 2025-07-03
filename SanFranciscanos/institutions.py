from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, abort
from sqlalchemy import text, exc
from .forms import (
    ArquidiocesisForm, VicariaForm, ParroquiaForm, 
    InstitutionRolSelectorForm, DeleteForm
)
import datetime

# Cambiamos el nombre del Blueprint para que sea único
bp = Blueprint('Institutions', __name__, url_prefix='/Institutions')

# ---#-!-# SECCIÓN DE CONFIGURACIÓN CENTRALIZADA PARA INSTITUCIONES ---
def get_institution_details(role):
    """
    Devuelve un diccionario centralizado con todos los detalles para un tipo de institución.
    Los nombres de las columnas están SINCRONIZADOS con las vistas SQL (v_Info...).
    """
    roles = {
        'Arquidiocesis': {
            'form': ArquidiocesisForm,
            'sp_insert': 'sp_InsertArquidiocesis',
            'sp_update': 'sp_UpdateArquidiocesis',
            'sp_delete': 'sp_DeleteArquidiocesis',
            'view': 'v_InfoArquidiocesis',
            'list_headers': ['ID Arquidiócesis', 'Nombre Arquidiócesis', 'Ciudad'],
            'detail_fields': {
                'ID Arquidiócesis': 'ID',
                'Nombre Arquidiócesis': 'Nombre',
                'Ciudad': 'Ciudad'
            },
            'fixed_params': {'type': 'Arquidiocesis'} # Parámetros fijos para el SP
        },
        'Vicaria': {
            'form': VicariaForm,
            'sp_insert': 'sp_InsertVicaria',
            'sp_update': 'sp_UpdateVicaria',
            'sp_delete': 'sp_DeleteVicaria',
            'view': 'v_InfoVicaria',
            'list_headers': ['ID Vicaria', 'Nombre Vicaria', 'Departamento', 'Nombre Arquidiócesis'],
            'detail_fields': {
                'ID Vicaria': 'ID',
                'Nombre Vicaria': 'Nombre',
                'Departamento': 'Departamento / Zona Pastoral',
                'Nombre Arquidiócesis': 'Pertenece a',
                'Ciudad Arquidiócesis': 'Ciudad de Arquidiócesis'
            },
            'fixed_params': {'type': 'Vicaria'}
        },
        'Parroquia': {
            'form': ParroquiaForm,
            'sp_insert': 'sp_InsertParroquia',
            'sp_update': 'sp_UpdateParroquia',
            'sp_delete': 'sp_DeleteParroquia',
            'view': 'v_InfoParroquia',
            'list_headers': ['ID Institución', 'Nombre Parroquia', 'Teléfono Parroquia', 'Nombre Vicaria'],
            'detail_fields': {
                'ID Institución': 'ID',
                'Nombre Parroquia': 'Nombre',
                'Dirección': 'Dirección Principal',
                'Teléfono Parroquia': 'Teléfono',
                'Nombre Vicaria': 'Pertenece a la Vicaria',
                'Nombre Arquidiócesis': 'Arquidiócesis'
            },
            'fixed_params': {'type': 'Parroquia'}
        }
    }
    return roles.get(role)

def load_institution_dynamic_choices(form, role, session):
    """Carga las opciones dinámicas para los SelectFields de los formularios de institución."""
    # Cargar Eclesiásticos (necesario para todos los formularios)
    query_ecl = text("SELECT ID, [Primer Nombre] + ' ' + [Primer Apellido] AS FullName FROM Persons.v_InfoEclesiastico WHERE Estado = 1 ORDER BY FullName")
    # Usamos .mappings().all() para obtener resultados como diccionarios
    eclesiasticos = session.execute(query_ecl).mappings().all()
    form.idEclesiastico.choices = [(e['ID'], e['FullName']) for e in eclesiasticos]
    form.idEclesiastico.choices.insert(0, ('', '-- Seleccione Responsable --'))

    if role == 'Vicaria':
        query = text("SELECT [ID Arquidiócesis], [Nombre Arquidiócesis] FROM Institutions.v_InfoArquidiocesis ORDER BY [Nombre Arquidiócesis]")
        # Usamos .mappings().all() para obtener resultados como diccionarios
        arqs = session.execute(query).mappings().all()
        form.idArquidiocesis.choices = [(a['ID Arquidiócesis'], a['Nombre Arquidiócesis']) for a in arqs]
        form.idArquidiocesis.choices.insert(0, ('', '-- Seleccione Arquidiócesis --'))
    
    if role == 'Parroquia':
        query = text("SELECT [ID Vicaria], [Nombre Vicaria] FROM Institutions.v_InfoVicaria ORDER BY [Nombre Vicaria]")
        # ---#-!-# LÍNEA CORREGIDA ---
        # Usamos .mappings().all() para obtener resultados como diccionarios
        vicarias = session.execute(query).mappings().all()
        form.idVicaria.choices = [(v['ID Vicaria'], v['Nombre Vicaria']) for v in vicarias]
        form.idVicaria.choices.insert(0, ('', '-- Seleccione Vicaria --'))

# --- Rutas ---

@bp.route('/', methods=['GET', 'POST'])
def index():
    form = InstitutionRolSelectorForm()
    if form.validate_on_submit():
        role = form.role.data
        return redirect(url_for('Institutions.list_institutions', role=role))
    return render_template('Institutions/select_role.html', form=form, title="Seleccionar Tipo de Institución")

@bp.route('/list/<role>')
def list_institutions(role):
    role_details = get_institution_details(role)
    if not role_details:
        abort(404)

    SessionLocal = current_app.SessionLocal
    session = SessionLocal()
    results = []
    delete_form = DeleteForm()
    try:
        # La consulta ahora apunta al esquema Institutions
        query = text(f"SELECT * FROM Institutions.{role_details['view']}")
        results = session.execute(query).mappings().fetchall()
    except exc.SQLAlchemyError as e:
        flash(f"Error al listar {role}s: {getattr(e, 'orig', e)}", 'danger')
    finally:
        session.close()

    return render_template(
        'Institutions/list.html',
        institutions=results, # Pasamos la lista con un nombre descriptivo
        headers=role_details['list_headers'],
        role=role,
        delete_form=delete_form,
        title=f"Lista de {role}s"
    )

@bp.route('/new/<role>', methods=['GET', 'POST'])
def new_institution(role):
    role_details = get_institution_details(role)
    if not role_details:
        abort(404)

    RoleForm = role_details['form']
    form = RoleForm()
    
    SessionLocal = current_app.SessionLocal
    session = SessionLocal()
    try:
        load_institution_dynamic_choices(form, role, session)
    finally:
        session.close()

    if form.validate_on_submit():
        params = {key: value for key, value in form.data.items() if key not in ['submit', 'csrf_token'] and value not in [None, '']}
        
        # Añadir parámetros fijos como 'type'
        params.update(role_details.get('fixed_params', {}))
        
        session = SessionLocal()
        try:
            output_param_name = "CreatedInstitutionID"
            param_placeholders = [f"@{k}=:{k}" for k in params.keys()]
            
            sql_string = f"""
                DECLARE @{output_param_name} INT;
                EXEC Institutions.{role_details['sp_insert']}
                    {', '.join(param_placeholders)},
                    @{output_param_name} = @{output_param_name} OUTPUT;
                SELECT @{output_param_name};
            """
            
            stmt = text(sql_string)
            created_id = session.execute(stmt, params).scalar_one()
            session.commit()
            
            flash(f'{role} creada exitosamente con ID: {created_id}.', 'success')
            return redirect(url_for('Institutions.list_institutions', role=role))

        except exc.SQLAlchemyError as e:
            if session.is_active:
                session.rollback()
            flash(f"Error de base de datos al crear {role}: {getattr(e, 'orig', e)}", 'danger')
        finally:
            session.close()

    return render_template(
        'Institutions/form.html',
        form=form,
        title=f'Nueva {role}',
        role=role,
        action_url=url_for('Institutions.new_institution', role=role)
    )

@bp.route('/edit/<role>/<int:institution_id>', methods=['GET', 'POST'])
def edit_institution(role, institution_id):
    role_details = get_institution_details(role)
    if not role_details:
        abort(404)

    RoleForm = role_details['form']
    SessionLocal = current_app.SessionLocal
    session = SessionLocal()
    
    try:
        # El ID puede tener nombres diferentes en cada vista ('ID Arquidiócesis', 'ID Vicaria', etc.)
        # Extraemos el primer header, que por convención es el ID
        id_column_name = role_details['list_headers'][0]
        query = text(f"SELECT * FROM Institutions.{role_details['view']} WHERE \"{id_column_name}\" = :id")
        institution_data = session.execute(query, {"id": institution_id}).mappings().fetchone()

        if not institution_data:
            flash(f"{role} con ID {institution_id} no encontrada.", 'warning')
            return redirect(url_for('Institutions.list_institutions', role=role))

        form = RoleForm(data=institution_data)
        load_institution_dynamic_choices(form, role, session)

        if form.validate_on_submit():
            params = {key: value for key, value in form.data.items() if key not in ['submit', 'csrf_token']}
            params['idInstitution'] = institution_id
            
            param_placeholders = [f"@{k}=:{k}" for k in params.keys()]
            sql_string = f"EXEC Institutions.{role_details['sp_update']} {', '.join(param_placeholders)}"

            try:
                session.execute(text(sql_string), params)
                session.commit()
                flash(f"{role} actualizada exitosamente.", 'success')
                return redirect(url_for('Institutions.list_institutions', role=role))
            except exc.SQLAlchemyError as e:
                session.rollback()
                flash(f"Error de base de datos al actualizar {role}: {getattr(e, 'orig', e)}", 'danger')

        return render_template(
            'Institutions/form.html',
            form=form,
            title=f'Editar {role}',
            role=role,
            action_url=url_for('Institutions.edit_institution', role=role, institution_id=institution_id)
        )
    finally:
        session.close()

@bp.route('/delete/<role>/<int:institution_id>', methods=['POST'])
def delete_institution(role, institution_id):
    role_details = get_institution_details(role)
    if not role_details or 'sp_delete' not in role_details:
        flash('Rol no reconocido para eliminación.', 'danger')
        return redirect(url_for('Institutions.index'))

    delete_form = DeleteForm()
    if not delete_form.validate_on_submit():
        flash('Intento de borrado no válido.', 'warning')
        return redirect(url_for('Institutions.list_institutions', role=role))

    SessionLocal = current_app.SessionLocal
    session = SessionLocal()
    try:
        sql_query = text(f"EXEC Institutions.{role_details['sp_delete']} @idInstitution = :id")
        session.execute(sql_query, {"id": institution_id})
        session.commit()
        flash(f'{role} con ID {institution_id} ha sido eliminada.', 'success')
    except exc.SQLAlchemyError as e:
        session.rollback()
        flash(f"Error de base de datos al eliminar {role}: {getattr(e, 'orig', e)}", 'danger')
    finally:
        session.close()

    return redirect(url_for('Institutions.list_institutions', role=role))

@bp.route('/<role>/<int:institution_id>')
def detail_institution(role, institution_id):
    role_details = get_institution_details(role)
    if not role_details:
        abort(404)

    SessionLocal = current_app.SessionLocal
    session = SessionLocal()
    detail_items = []
    
    try:
        id_column_name = role_details['list_headers'][0]
        query = text(f"SELECT * FROM Institutions.{role_details['view']} WHERE \"{id_column_name}\" = :id")
        institution_data = session.execute(query, {"id": institution_id}).mappings().fetchone()

        if not institution_data:
            flash(f"{role} con ID {institution_id} no encontrada.", 'warning')
            return redirect(url_for('Institutions.list_institutions', role=role))

        for column_name, label in role_details['detail_fields'].items():
            if column_name in institution_data:
                value = institution_data[column_name]
                detail_items.append((label, value if value is not None else 'N/A'))
            
    except exc.SQLAlchemyError as e:
        flash(f"Error al ver detalle de {role}: {getattr(e, 'orig', e)}", 'danger')
        return redirect(url_for('Institutions.list_institutions', role=role))
    finally:
        session.close()

    return render_template(
        'Institutions/detail.html',
        detail_items=detail_items,
        title=f"Detalle de {role}",
        role=role,
        institution_id=institution_id
    )