from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, abort
from sqlalchemy import text, exc, select
from .forms import (
    CatequistaForm, AyudanteForm, EclesiasticoForm, PadrinoForm,
    PadreMadreForm, RolSelectorForm, DeleteForm
)
from .models import Person, Catequista, Ayudante, Eclesiastico, Padrino, Parent, Institution, Catequizado
import datetime
bp = Blueprint('Persons', __name__, url_prefix='/Persons')

# --- Función Auxiliar Centralizada ---


def get_role_details(role):
    """
    Devuelve un diccionario centralizado con todos los detalles necesarios para un rol,
    incluyendo formularios, modelos, plantillas, nombres de SP y configuraciones de vista.
    """
    roles = {
        'Catequista': {
            'form': CatequistaForm,
            'model': Catequista,
            'template': 'Persons/form.html',
            'list_template': 'Persons/list.html',
            'detail_template': 'Persons/detail.html',
            'sp_insert': 'sp_InsertCatequista',
            'sp_update': 'sp_UpdateCatequista', # Asumiendo que existe este SP
            'sp_delete': 'sp_DeleteCatequista', # Asumiendo que existe este SP
            'view': 'v_InfoCatequista',
            'list_headers': ['ID', 'Primer Nombre', 'Primer Apellido', 'Anios De Exp'],
            'detail_fields': {
                'ID': 'ID de Catequista',
                'Primer Nombre': 'Primer Nombre',
                'Segundo Nombre': 'Segundo Nombre',
                'Primer Apellido': 'Primer Apellido',
                'Segundo Apellido': 'Segundo Apellido',
                'Sexo': 'Sexo',
                'Anios De Exp': 'Años de Experiencia',
                'Estado': 'Estado' # Asumiendo que tu vista lo devuelve
            }
        },
        'Ayudante': {
            'form': AyudanteForm,
            'model': Ayudante,
            'template': 'Persons/form.html',
            'list_template': 'Persons/list.html',
            'detail_template': 'Persons/detail.html',
            'sp_insert': 'sp_InsertAyudante',
            'sp_update': 'sp_UpdateAyudante',
            'sp_delete': 'sp_DeleteAyudante',
            'view': 'v_InfoAyudante',
            # ¡Verifica estos nombres de columna con tu vista v_InfoAyudante!
            'list_headers': ['ID', 'PrimerNombre', 'PrimerApellido', 'Desde'],
            'detail_fields': {
                'ID': 'ID de Ayudante',
                'PrimerNombre': 'Primer Nombre',
                'SegundoNombre': 'Segundo Nombre',
                'PrimerApellido': 'Primer Apellido',
                'SegundoApellido': 'Segundo Apellido',
                'Sexo': 'Sexo',
                'Desde': 'Voluntario Desde'
            }
        },
        'Eclesiastico': {
            'form': EclesiasticoForm,
            'model': Eclesiastico,
            'template': 'Persons/form.html',
            'list_template': 'Persons/list.html',
            'detail_template': 'Persons/detail.html',
            'sp_insert': 'sp_InsertEclesiastico',
            'sp_update': 'sp_UpdateEclesiastico',
            'sp_delete': 'sp_DeleteEclesiastico',
            'view': 'v_InfoEclesiastico',
            'list_headers': ['ID', 'PrimerNombre', 'Rol', 'Institucion'],
            'detail_fields': {
                'ID': 'ID de Eclesiástico',
                'PrimerNombre': 'Primer Nombre',
                'PrimerApellido': 'Primer Apellido',
                'Rol': 'Rol',
                'Institucion': 'Institución Asignada',
                'Estado': 'Estado'
            }
        },
        'Padrino': {
            'form': PadrinoForm,
            'model': Padrino,
            'template': 'Persons/form.html',
            'list_template': 'Persons/list.html',
            'detail_template': 'Persons/detail.html',
            'sp_insert': 'sp_InsertPadrino',
            'sp_update': 'sp_UpdatePadrino',
            'sp_delete': 'sp_DeletePadrino',
            'view': 'v_InfoPadrino',
            'list_headers': ['ID', 'PrimerNombre', 'PrimerApellido', 'Ocupacion'],
            'detail_fields': {
                'ID': 'ID de Padrino',
                'PrimerNombre': 'Primer Nombre',
                'PrimerApellido': 'Primer Apellido',
                'Sexo': 'Sexo',
                'Ocupacion': 'Ocupación'
            }
        },
        'PadreMadre': {
            'form': PadreMadreForm,
            'model': Parent,
            'template': 'Persons/form.html',
            'list_template': 'Persons/list.html',
            'detail_template': 'Persons/detail.html',
            'sp_insert': 'sp_InsertParent',
            'sp_update': 'sp_UpdateParent',
            'sp_delete': 'sp_DeleteParent',
            'view': 'v_InfoParent', # Asegúrate de tener esta vista
            'list_headers': ['ID', 'Primer Nombre', 'Primer Apellido', 'Ocupación'],
            'detail_fields': {
                'ID': 'ID de Padre/Madre',
                'Primer Nombre': 'Primer Nombre',
                'Segundo Nombre': 'Segundo Nombre',
                'Primer Apellido': 'Primer Apellido',
                'Segundo Apellido': 'Segundo Apellido',
                'Sexo': 'Sexo',
                'Ocupación': 'Ocupación',
                'Teléfono de Contacto': 'Teléfono',
                'Email de Contacto': 'Email',
                'ID Catequizado': 'ID del Catequizado Asociado'
            }
        }
    }
    return roles.get(role)

def load_dynamic_choices(form, role, session):
    """
    Carga las opciones dinámicas para los SelectFields de un formulario.
    """
    if role == 'PadreMadre':
        # Consulta para obtener ID y nombre completo de todos los catequizados
        catequizados = session.execute(
            select(Person.idPerson, Person.firstName, Person.lastName).join(Catequizado)
        ).all()
        form.idCatequizado.choices = [
            (c.idPerson, f"{c.firstName} {c.lastName}") for c in catequizados
        ]
        form.idCatequizado.choices.insert(0, ('', '-- Seleccione un Catequizado --'))
    
    if role == 'Eclesiastico':
        # Cargar lista de instituciones
        institutions = session.execute(select(Institution.idInstitution, Institution.name)).all()
        form.idInstitution.choices = [
            (i.idInstitution, i.name) for i in institutions
        ]
        form.idInstitution.choices.insert(0, ('', '-- Seleccione una Institución --'))

# --- Rutas ---

@bp.route('/', methods=['GET', 'POST'])
def index():
    form = RolSelectorForm()
    if form.validate_on_submit():
        role = form.role.data
        return redirect(url_for('Persons.list_persons', role=role))
    return render_template('Persons/select_role.html', form=form, title="Seleccionar Rol")

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

    # --- CAMBIO PRINCIPAL: USAR LA PLANTILLA GENÉRICA ---
    return render_template(
        'Persons/list.html', # Usar la nueva plantilla genérica
        persons=results,
        headers=role_details['list_headers'], # Pasar los encabezados dinámicamente
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
    sp_name = role_details['sp_insert']
    
    form = RoleForm()
    
    SessionLocal = current_app.SessionLocal
    session = SessionLocal()
    try:
        load_dynamic_choices(form, role, session)
    finally:
        session.close()

    if form.validate_on_submit():
        # ... (La lógica de inserción se mantiene igual) ...
        pass
        
    # --- CAMBIO PRINCIPAL: USAR LA PLANTILLA GENÉRICA ---
    return render_template(
        'Persons/form.html', # Usar la nueva plantilla genérica
        form=form,
        title=f'Nuevo {role}',
        role=role, # Pasar el rol para el botón de cancelar
        action_url=url_for('Persons.new_person', role=role)
    )

@bp.route('/edit/<role>/<int:person_id>', methods=['GET', 'POST'])
def edit_person(role, person_id):
    role_details = get_role_details(role)
    if not role_details:
        abort(404)

    RoleModel = role_details['model']
    RoleForm = role_details['form']
    
    SessionLocal = current_app.SessionLocal
    session = SessionLocal()
    
    person_to_edit = session.get(RoleModel, person_id)

    if not person_to_edit:
        # ... (manejo de no encontrado) ...
        pass
    
    form = RoleForm(obj=person_to_edit)
    load_dynamic_choices(form, role, session)

    if form.validate_on_submit():
        # ... (la lógica de actualización ORM se mantiene igual) ...
        pass

    if session.is_active:
        session.close()

    # --- CAMBIO PRINCIPAL: USAR LA PLANTILLA GENÉRICA ---
    return render_template(
        'Persons/form.html', # Usar la nueva plantilla genérica
        form=form,
        title=f'Editar {role}',
        role=role, # Pasar el rol para el botón de cancelar
        action_url=url_for('Persons.edit_person', role=role, person_id=person_id)
    )

@bp.route('/delete/<role>/<int:person_id>', methods=['POST'])
def delete_person(role, person_id):
    role_details = get_role_details(role)
    if not role_details or 'sp_delete' not in role_details:
        flash('Rol no reconocido para eliminación.', 'danger')
        return redirect(url_for('Persons.index'))

    sp_delete_name = role_details['sp_delete']
    SessionLocal = current_app.SessionLocal
    session = SessionLocal()
    try:
        # Estandarizar el nombre del parámetro. Si tus SPs esperan @idToDelete o @idPersonToDelete, úsalo.
        sql_query = text(f"EXEC Persons.{sp_delete_name} @idToDelete = :id")
        session.execute(sql_query, {"id": person_id})
        session.commit()
        flash(f'{role} con ID {person_id} ha sido eliminado.', 'success')
    except exc.SQLAlchemyError as e:
        session.rollback()
        flash(f"Error de base de datos al eliminar {role}: {e.orig}", 'danger')
        print(f"Error en SP DELETE para {role}: {e}")
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
    detail_items = [] # Inicializar como lista vacía
    
    try:
        query = text(f"SELECT * FROM Persons.{role_details['view']} WHERE ID = :id")
        result_proxy = session.execute(query, {"id": person_id})
        person_data = result_proxy.mappings().fetchone()

        if not person_data:
            flash(f"{role} con ID {person_id} no encontrado.", 'warning')
            return redirect(url_for('Persons.list_persons', role=role))

        # --- LÓGICA PRINCIPAL: CONSTRUIR LA LISTA DE DETALLES ---
        # Iterar sobre el diccionario de 'detail_fields' para asegurar el orden y las etiquetas correctas.
        for column_name, label in role_details['detail_fields'].items():
            if column_name in person_data:
                value = person_data[column_name]
                
                # Lógica de formato especial para ciertos campos
                if column_name == 'Sexo':
                    value = 'Masculino' if value == 'M' else ('Femenino' if value == 'F' else value)
                elif column_name == 'Estado':
                    value = 'Activo' if value else 'Inactivo'
                elif isinstance(value, datetime.date):
                    # Formatear la fecha si se está usando Flask-Moment
                    # Si no, se mostrará como YYYY-MM-DD
                    pass # Se puede manejar en la plantilla o aquí

                detail_items.append((label, value))
            
    except exc.SQLAlchemyError as e:
        flash(f"Error al ver detalle de {role}: {e.orig}", 'danger')
        return redirect(url_for('Persons.list_persons', role=role))
    finally:
        session.close()

    return render_template(
        'Persons/detail.html', # Usar la nueva plantilla genérica
        detail_items=detail_items,
        title=f"Detalle de {role}",
        role=role
    )