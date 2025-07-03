from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, abort,jsonify
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

@bp.route('/check_dependencies/<int:institution_id>', methods=['GET'])
def check_dependencies(institution_id):
    SessionLocal = current_app.SessionLocal
    session = SessionLocal()
    try:
        sp_sql = text("EXEC Institutions.sp_CheckInstitutionDependencies @idInstitution=:id")
        dependencies = session.execute(sp_sql, {"id": institution_id}).mappings().all()
        
        if dependencies:
            # Si hay dependencias, las agrupamos y las devolvemos
            grouped_deps = {}
            for dep in dependencies:
                if dep['DependencyType'] not in grouped_deps:
                    grouped_deps[dep['DependencyType']] = []
                grouped_deps[dep['Description']] = dep['Description'] # Usamos la descripción como clave para evitar duplicados visuales
            
            # Formateamos para el modal
            dependency_list = []
            for dep_type, descs in grouped_deps.items():
                if isinstance(descs, list): # Agrupación original
                    dependency_list.append(f"<strong>{dep_type}:</strong><ul>{''.join(f'<li>{d}</li>' for d in descs)}</ul>")
            
            # Corrección para la nueva lógica de agrupamiento
            formatted_deps = {}
            for dep in dependencies:
                dep_type = dep['DependencyType']
                desc = dep['Description']
                if dep_type not in formatted_deps:
                    formatted_deps[dep_type] = []
                formatted_deps[dep_type].append(desc)
            
            html_list = ""
            for dep_type, desc_list in formatted_deps.items():
                html_list += f"<p><strong>{dep_type} dependientes:</strong></p><ul class='list-group list-group-flush mb-3'>"
                for desc in desc_list:
                    html_list += f"<li class='list-group-item py-1'>{desc}</li>"
                html_list += "</ul>"

            return jsonify({
                'can_delete': False,
                'message': "No se puede eliminar esta institución porque otros registros dependen de ella. Debe eliminar o reasignar las siguientes dependencias primero:",
                'dependencies_html': html_list
            })
        else:
            # Si no hay dependencias, se puede borrar
            return jsonify({'can_delete': True})
    except exc.SQLAlchemyError as e:
        return jsonify({'can_delete': False, 'message': f"Error al verificar dependencias: {e}"}), 500
    finally:
        session.close()

# ---#-!-# RUTA DE BORRADO MODIFICADA ---
@bp.route('/delete/<role>/<int:institution_id>', methods=['POST'])
def delete_institution(role, institution_id):
    role_details = get_institution_details(role)
    if not role_details:
        return jsonify({'success': False, 'message': 'Rol no reconocido.'}), 404

    SessionLocal = current_app.SessionLocal
    session = SessionLocal()
    try:
        sql_query = text(f"EXEC Institutions.{role_details['sp_delete']} @idInstitution = :id")
        session.execute(sql_query, {"id": institution_id})
        session.commit()
        return jsonify({
            'success': True, 
            'message': f'{role} con ID {institution_id} ha sido eliminada exitosamente.'
        })

    except exc.SQLAlchemyError as e:
        if session.is_active: session.rollback()
        # Este es un error de fallback, la verificación debería haberlo prevenido.
        return jsonify({'success': False, 'message': 'Error inesperado al intentar borrar. Es posible que hayan surgido nuevas dependencias.'}), 400
    finally:
        if session.is_active: session.close()

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