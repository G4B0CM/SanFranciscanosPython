# backend/persons.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, abort
from sqlalchemy import text, exc, select, func
from .forms import (
    CatequistaForm, AyudanteForm, EclesiasticoForm, PadrinoForm,
    PadreMadreForm, RolSelectorForm, DeleteForm, CatequizadoForm
)
from .models import Person, Catequista, Ayudante, Eclesiastico, Padrino, Parent, Institution, Catequizado
import datetime

bp = Blueprint('Persons', __name__, url_prefix='/Persons')

# ---#-!-# SECCIÓN DE CONFIGURACIÓN CENTRALIZADA (CORREGIDA Y SINCRONIZADA) ---
def get_role_details(role):
    """
    Devuelve un diccionario centralizado con todos los detalles necesarios para un rol.
    Los nombres de las columnas están SINCRONIZADOS con las vistas SQL (v_Info...).
    """
    roles = {
         'Catequizado': {
            'form': CatequizadoForm,
            'template': 'Persons/form.html',
            'sp_insert': 'sp_InsertCatequizado',
            'sp_update': 'sp_UpdateCatequizado',
            'sp_delete': 'sp_DeleteCatequizado',
            'view': 'v_InfoCatequizado',
            'list_headers': ['ID', 'Primer Nombre', 'Primer Apellido', 'Fecha de Nacimiento', 'Estado'],
            'detail_fields': {
                'ID': 'ID de Catequizado',
                'Primer Nombre': 'Primer Nombre',
                'Segundo Nombre': 'Segundo Nombre',
                'Primer Apellido': 'Primer Apellido',
                'Segundo Apellido': 'Segundo Apellido',
                'Fecha de Nacimiento': 'Fecha de Nacimiento',
                'Sexo': 'Sexo',
                'Tipo de sangre': 'Tipo de Sangre',
                'Alergias': 'Alergias',
                'Nombre Contacto de Emergencia': 'Contacto de Emergencia (Nombre)',
                'Número de Contacto de Emergencia': 'Contacto de Emergencia (Teléfono)',
                'Detalles': 'Detalles Adicionales',
                'Estado': 'Estado'
            },
            'field_mapping': {
                'firstName': 'Primer Nombre',
                'secondName': 'Segundo Nombre',
                'lastName': 'Primer Apellido',
                'secondLastName': 'Segundo Apellido',
                'birthDate': 'Fecha de Nacimiento',
                'sex': 'Sexo',
                'bloodType': 'Tipo de sangre',
                'allergies': 'Alergias',
                'emergencyContactName': 'Nombre Contacto de Emergencia',
                'emergencyContactPhone': 'Número de Contacto de Emergencia',
                'details': 'Detalles',
                'state': 'Estado'
            }
        },
        'Catequista': {
            'form': CatequistaForm,
            'template': 'Persons/form.html',
            'sp_insert': 'sp_InsertCatequista',
            'sp_update': 'sp_UpdateCatequista',
            'sp_delete': 'sp_DeleteCatequista',
            'view': 'v_InfoCatequista',
            'list_headers': ['ID', 'Primer Nombre', 'Primer Apellido', 'Años De Exp', 'Estado'],
            'detail_fields': {
                'ID': 'ID de Catequista',
                'Primer Nombre': 'Primer Nombre',
                'Segundo Nombre': 'Segundo Nombre',
                'Primer Apellido': 'Primer Apellido',
                'Segundo Apellido': 'Segundo Apellido',
                'Sexo': 'Sexo',
                'Años De Exp': 'Años de Experiencia',
                'Estado': 'Estado'
            },
            'field_mapping': {
                'firstName': 'Primer Nombre',
                'secondName': 'Segundo Nombre',
                'lastName': 'Primer Apellido',
                'secondLastName': 'Segundo Apellido',
                'sex': 'Sexo',
                'yearsOfExp': 'Años De Exp',
                'state': 'Estado'
            }
        },
        'Ayudante': {
            'form': AyudanteForm,
            'template': 'Persons/form.html',
            'sp_insert': 'sp_InsertAyudante',
            'sp_update': 'sp_UpdateAyudante', 
            'sp_delete': 'sp_DeleteAyudante',
            'view': 'v_InfoAyudante',
            'list_headers': ['ID', 'Primer Nombre', 'Primer Apellido', 'Voluntario Desde'],
            'detail_fields': {
                'ID': 'ID de Ayudante',
                'Primer Nombre': 'Primer Nombre',
                'Segundo Nombre': 'Segundo Nombre',
                'Primer Apellido': 'Primer Apellido',
                'Segundo Apellido': 'Segundo Apellido',
                'Sexo': 'Sexo',
                'Voluntario Desde': 'Voluntario Desde'
            },
            'field_mapping': {
                'firstName': 'Primer Nombre',
                'secondName': 'Segundo Nombre',
                'lastName': 'Primer Apellido',
                'secondLastName': 'Segundo Apellido',
                'sex': 'Sexo',
                'volunteerSince': 'Voluntario Desde'
            }
        },
        'Eclesiastico': {
            'form': EclesiasticoForm,
            'template': 'Persons/form.html',
            'sp_insert': 'sp_InsertEclesiastico',
            'sp_update': 'sp_UpdateEclesiastico',
            'sp_delete': 'sp_DeleteEclesiastico',
            'view': 'v_InfoEclesiastico',
            'list_headers': ['ID', 'Primer Nombre', 'Rol', 'Estado'],
            'detail_fields': {
                'ID': 'ID de Eclesiástico',
                'Primer Nombre': 'Primer Nombre',
                'Segundo Nombre': 'Segundo Nombre',
                'Primer Apellido': 'Primer Apellido',
                'Segundo Apellido': 'Segundo Apellido',
                'Sexo': 'Sexo',
                'Rol': 'Rol',
                'Estado': 'Estado'
            },
            'field_mapping': {
                'firstName': 'Primer Nombre',
                'secondName': 'Segundo Nombre',
                'lastName': 'Primer Apellido',
                'secondLastName': 'Segundo Apellido',
                'sex': 'Sexo',
                'role': 'Rol',
                'state': 'Estado',
                'idInstitution': 'idInstitution'
            }
        },
        'Padrino': {
            'form': PadrinoForm,
            'template': 'Persons/form.html',
            'sp_insert': 'sp_InsertPadrino',
            'sp_update': 'sp_UpdatePadrino',
            'sp_delete': 'sp_DeletePadrino',
            'view': 'v_InfoPadrino',
            'list_headers': ['ID', 'Primer Nombre', 'Primer Apellido', 'Ocupacion'],
            'detail_fields': {
                'ID': 'ID de Padrino',
                'Primer Nombre': 'Primer Nombre',
                'Segundo Nombre': 'Segundo Nombre',
                'Primer Apellido': 'Primer Apellido',
                'Segundo Apellido': 'Segundo Apellido',
                'Sexo': 'Sexo',
                'Ocupacion': 'Ocupación'
            },
            'field_mapping': {
                'firstName': 'Primer Nombre',
                'secondName': 'Segundo Nombre',
                'lastName': 'Primer Apellido',
                'secondLastName': 'Segundo Apellido',
                'sex': 'Sexo',
                'occupation': 'Ocupacion'
            }
        },
        'PadreMadre': {
            'form': PadreMadreForm,
            'model': Parent, # Se mantiene para la carga de datos del hijo
            'template': 'Persons/form.html',
            'sp_insert': 'sp_InsertParent',
            'sp_update': 'sp_UpdateParent',
            'sp_delete': 'sp_DeleteParent',
            'view': 'v_InfoParent',
            'list_headers': ['ID', 'Primer Nombre', 'Primer Apellido', 'Ocupacion', 'Hijo(a) a cargo'],
            'detail_fields': {
                'ID': 'ID de Padre/Madre',
                'Primer Nombre': 'Primer Nombre',
                'Segundo Nombre': 'Segundo Nombre',
                'Primer Apellido': 'Primer Apellido',
                'Segundo Apellido': 'Segundo Apellido',
                'Sexo': 'Sexo',
                'Ocupacion': 'Ocupación',
                'Telefono': 'Teléfono',
                'Email': 'Email',
                'Hijo(a) a cargo': 'Hijo(a) a cargo'
            },
            'field_mapping': {
                'firstName': 'Primer Nombre',
                'secondName': 'Segundo Nombre',
                'lastName': 'Primer Apellido',
                'secondLastName': 'Segundo Apellido',
                'sex': 'Sexo',
                'occupation': 'Ocupacion',
                'phone': 'Telefono',
                'email': 'Email',
                'idCatequizado': 'ID Hijo'
            }
        }
    }
    return roles.get(role)

def load_dynamic_choices(form, role, session):
    """Carga las opciones dinámicas para los SelectFields de un formulario."""
    if role == 'PadreMadre':
        # Consulta para obtener ID y nombre completo de todos los catequizados activos
        query = text("SELECT ID, [Primer Nombre], [Primer Apellido] FROM Persons.v_InfoCatequizado WHERE Estado = 1 ORDER BY [Primer Apellido], [Primer Nombre]")
        catequizados = session.execute(query).mappings().all()
        form.idCatequizado.choices = [
            (c.ID, f"{c['Primer Nombre']} {c['Primer Apellido']}") for c in catequizados
        ]
        form.idCatequizado.choices.insert(0, ('', '-- Seleccione un Catequizado --'))
    
    #-!-# LÓGICA AGREGADA PARA CARGAR INSTITUCIONES
    if role == 'Eclesiastico':
        query = text("SELECT idInstitution, name FROM Institutions.Institution ORDER BY name")
        institutions = session.execute(query).all()
        form.idInstitution.choices = [
            (i.idInstitution, i.name) for i in institutions
        ]
        form.idInstitution.choices.insert(0, ('', '-- Sin Institución Asignada --'))

# --- Rutas ---

@bp.route('/', methods=['GET', 'POST'])
def index():
    form = RolSelectorForm()
    if form.validate_on_submit():
        role = form.role.data
        return redirect(url_for('Persons.list_persons', role=role))
    return render_template('Persons/select_role.html', form=form, title="Seleccionar Rol de Persona")

@bp.route('/list/<role>')
def list_persons(role):
    role_details = get_role_details(role)
    if not role_details:
        abort(404)

    SessionLocal = current_app.SessionLocal
    session = SessionLocal()
    results = []
    delete_form = DeleteForm()
    try:
        query = text(f"SELECT * FROM Persons.{role_details['view']}")
        results = session.execute(query).mappings().fetchall()
    except exc.SQLAlchemyError as e:
        flash(f"Error al listar {role}s: {e.orig}", 'danger')
    finally:
        session.close()

    return render_template(
        'Persons/list.html',
        persons=results, # <--- ¡CORREGIDO! ahora se llama 'persons'
        headers=role_details['list_headers'],
        role=role,
        delete_form=delete_form,
        title=f"Lista de {role}s"
    )

@bp.route('/new/<role>', methods=['GET', 'POST'])
def new_person(role):
    role_details = get_role_details(role)
    if not role_details:
        abort(404)

    RoleForm = role_details['form']
    form = RoleForm()
    
    SessionLocal = current_app.SessionLocal
    session = SessionLocal()
    try:
        load_dynamic_choices(form, role, session)
    finally:
        session.close() # Cerramos la sesión usada para cargar choices

    if form.validate_on_submit():
        # Recolectar parámetros del formulario, excluyendo los que no van al SP
        params = {
            key: value for key, value in form.data.items()
            if key not in ['submit', 'csrf_token'] and value not in [None, '']
        }
        
        # Asegurarse de que los valores booleanos 'state' se envíen si el formulario no los incluye
        if role in ['Catequista', 'Eclesiastico'] and 'state' not in params:
             params['state'] = form.state.data # Usar el valor del campo, incluso si es False
        
        session = SessionLocal()
        try:
            # ---#-!-# LÓGICA CORRECTA PARA LLAMAR SP CON PARÁMETRO OUTPUT ---

            # 1. Nombre del parámetro de salida que definimos en TODOS los SPs
            output_param_name = "CreatedPersonID"
            
            # 2. Lista de placeholders para los parámetros de ENTRADA
            # Ej: ['@firstName=:firstName', '@lastName=:lastName']
            param_placeholders = [f"@{k}=:{k}" for k in params.keys()]
            
            # 3. Construir el string SQL completo.
            #    - DECLARE: Crea una variable temporal en SQL Server para recibir el valor.
            #    - EXEC: Llama al SP, pasando los parámetros de entrada y diciéndole
            #            que ponga el valor de salida en nuestra variable temporal.
            #    - SELECT: Devuelve el valor de la variable temporal como resultado de la consulta.
            sql_string = f"""
                DECLARE @{output_param_name} INT;
                EXEC Persons.{role_details['sp_insert']}
                    {', '.join(param_placeholders)},
                    @{output_param_name} = @{output_param_name} OUTPUT;
                SELECT @{output_param_name};
            """
            
            # 4. Ejecutar la consulta y obtener el resultado.
            #    - text() prepara el string SQL.
            #    - session.execute() lo envía a la BD junto con los valores de `params`.
            #    - .scalar_one() es perfecto para obtener un único valor de una única fila.
            stmt = text(sql_string)
            created_id = session.execute(stmt, params).scalar_one()
            
            session.commit() # Si todo fue bien, confirmar la transacción.
            
            flash(f'{role} creado exitosamente con ID: {created_id}.', 'success')
            return redirect(url_for('Persons.list_persons', role=role))

        except exc.SQLAlchemyError as e:
            if session.is_active:
                session.rollback()
            # Usamos getattr para obtener el error original, que es más descriptivo
            flash(f"Error de base de datos al crear {role}: {getattr(e, 'orig', e)}", 'danger')
        finally:
            session.close()

    # Si el formulario no es válido o es una petición GET, renderizar la plantilla
    return render_template(
        role_details['template'],
        form=form,
        title=f'Nuevo {role}',
        role=role,
        action_url=url_for('Persons.new_person', role=role)
    )

@bp.route('/edit/<role>/<int:person_id>', methods=['GET', 'POST'])
def edit_person(role, person_id):
    role_details = get_role_details(role)
    if not role_details:
        abort(404)

    RoleForm = role_details['form']
    SessionLocal = current_app.SessionLocal
    session = SessionLocal()

    try:
        # 1. Obtener datos del registro desde la vista SQL
        query = text(f"SELECT * FROM Persons.{role_details['view']} WHERE ID = :id")
        person_data = session.execute(query, {"id": person_id}).mappings().fetchone()

        if not person_data:
            flash(f"{role} con ID {person_id} no encontrado.", 'warning')
            return redirect(url_for('Persons.list_persons', role=role))

        # 2. Preparar mapeo para precargar el formulario
        field_mapping = role_details.get('field_mapping', {})
        mapped_data = {
            form_field: person_data.get(view_column)
            for form_field, view_column in field_mapping.items()
        }

        # Convertir valores booleanos si es necesario (ejemplo: Estado)
        if 'state' in mapped_data and mapped_data['state'] is not None:
            mapped_data['state'] = bool(mapped_data['state'])

        # 3. Precargar el formulario con los datos mapeados
        form = RoleForm(data=mapped_data)
        load_dynamic_choices(form, role, session)

        # 4. Si se envía el formulario (POST), procesar la actualización
        if form.validate_on_submit():
            params = {
                key: value for key, value in form.data.items()
                if key not in ['submit', 'csrf_token']
            }
            params['idPerson'] = person_id  # Parámetro obligatorio para el SP de actualización

            param_placeholders = [f"@{k}=:{k}" for k in params.keys()]
            sql_string = f"EXEC Persons.{role_details['sp_update']} {', '.join(param_placeholders)}"

            try:
                session.execute(text(sql_string), params)
                session.commit()
                flash(f"{role} actualizado exitosamente.", 'success')
                return redirect(url_for('Persons.list_persons', role=role))
            except exc.SQLAlchemyError as e:
                session.rollback()
                flash(f"Error de base de datos al actualizar {role}: {getattr(e, 'orig', e)}", 'danger')

        # Renderizar la plantilla con el formulario precargado
        return render_template(
            role_details['template'],
            form=form,
            title=f'Editar {role}',
            role=role,
            action_url=url_for('Persons.edit_person', role=role, person_id=person_id)
        )

    finally:
        session.close()

@bp.route('/delete/<role>/<int:person_id>', methods=['POST'])
def delete_person(role, person_id):
    role_details = get_role_details(role)
    if not role_details or 'sp_delete' not in role_details:
        flash('Rol no reconocido para eliminación.', 'danger')
        return redirect(url_for('Persons.index'))

    delete_form = DeleteForm()
    if not delete_form.validate_on_submit():
        flash('Intento de borrado no válido.', 'warning')
        return redirect(url_for('Persons.list_persons', role=role))

    SessionLocal = current_app.SessionLocal
    session = SessionLocal()
    try:
        #-!-# Parámetro estandarizado a @idPerson
        sql_query = text(f"EXEC Persons.{role_details['sp_delete']} @idPerson = :id")
        session.execute(sql_query, {"id": person_id})
        session.commit()
        flash(f'{role} con ID {person_id} ha sido eliminado/desactivado.', 'success')
    except exc.SQLAlchemyError as e:
        session.rollback()
        flash(f"Error de base de datos al eliminar {role}: {getattr(e, 'orig', e)}", 'danger')
    finally:
        session.close()

    return redirect(url_for('Persons.list_persons', role=role))


@bp.route('/<role>/<int:person_id>')
def detail_person(role, person_id):
    role_details = get_role_details(role)
    if not role_details:
        abort(404)

    SessionLocal = current_app.SessionLocal
    session = SessionLocal()
    detail_items = []
    
    try:
        query = text(f"SELECT * FROM Persons.{role_details['view']} WHERE ID = :id")
        person_data = session.execute(query, {"id": person_id}).mappings().fetchone()

        if not person_data:
            flash(f"{role} con ID {person_id} no encontrado.", 'warning')
            return redirect(url_for('Persons.list_persons', role=role))

        #-!-# Iterar sobre la configuración para asegurar orden y etiquetas correctas
        for column_name, label in role_details['detail_fields'].items():
            if column_name in person_data:
                value = person_data[column_name]
                
                # Formato especial de valores para visualización
                if column_name == 'Sexo' and value in ['M', 'F']:
                    value = 'Masculino' if value == 'M' else 'Femenino'
                elif column_name == 'Estado':
                    value = 'Activo' if value else 'Inactivo'
                elif isinstance(value, datetime.date):
                    value = value.strftime('%d-%m-%Y') # Formato legible
                
                detail_items.append((label, value if value is not None else 'N/A'))
            
    except exc.SQLAlchemyError as e:
        flash(f"Error al ver detalle de {role}: {getattr(e, 'orig', e)}", 'danger')
        return redirect(url_for('Persons.list_persons', role=role))
    finally:
        session.close()

    return render_template(
        'Persons/detail.html',
        detail_items=detail_items,
        title=f"Detalle de {role}",
        role=role,
        person_id=person_id # Pasar el ID para los botones de acción
    )