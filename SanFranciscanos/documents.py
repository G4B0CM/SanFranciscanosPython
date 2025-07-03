# backend/documents.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, abort
from sqlalchemy import text, exc
from .forms import (
    DocumentRolSelectorForm, DataSheetForm, PaymentForm, AttendanceForm, DeleteForm,
    AcreditationForm, BautismFaithForm, LevelAprobationForm, LevelCertificateForm
)
import datetime

bp = Blueprint('Documents', __name__, url_prefix='/Documents')

def get_item_details(role):
    """Devuelve la configuración COMPLETA para cada tipo de documento."""
    # Nota: Los 'field_map' son cruciales para la edición. Mapean Clave_de_Vista -> Nombre_de_Campo_Formulario
    roles = {
        'DataSheet': {
            'form': DataSheetForm, 'sp_insert': 'sp_InsertDataSheet', 'sp_update': 'sp_UpdateDataSheet',
            'sp_delete': 'sp_DeleteDataSheet', 'view': 'v_InfoDataSheet',
            'list_headers': ['idDataSheet', 'Primer Nombre Catequizado', 'Primer Apellido Catequizado', 'Curso Escolar'],
            'output_param': 'CreatedDataSheetID', 'id_param': 'idDataSheet',
            # ---#-!-# MAPA DE CAMPO COMPLETO PARA DATASHEET ---
            'field_map': {
                'Primer Nombre Catequizado': 'c_firstName', 'Segundo Nombre Catequizado': 'c_secondName',
                'Primer Apellido Catequizado': 'c_lastName', 'Segundo Apellido Catequizado': 'c_secondLastName',
                'Sexo Catequizado': 'c_sex', 'Nacimiento Catequizado': 'c_birthdate',
                'Tipo de sangre': 'c_bloodType', 'Alergias': 'c_alergies',
                'Contacto de emergencia': 'c_emergencyContactName', 'Teléfono de contacto de emergencia': 'c_emergencyContactPhone',
                'Detalles Salud/Otros Catequizado': 'c_details',
                
                'Primer Nombre Parent': 'f_firstName', 'Segundo Nombre Parent': 'f_secondName',
                'Apellido Paterno Parent': 'f_lastName', 'Apellido Materno Parent': 'f_secondLastName',
                'Ocupación Parent': 'f_ocupation', 'Teléfono Parent': 'f_phoneContact', 'Email Parent': 'f_emailContact',
                
                'Primer Nombre Madre': 'm_firstName', 'Segundo Nombre Madre': 'm_secondName',
                'Apellido Paterno Madre': 'm_lastName', 'Apellido Materno Madre': 'm_secondLastName',
                'Ocupación Madre': 'm_ocupation', 'Teléfono Madre': 'm_phoneContact', 'Email Madre': 'm_emailContact',

                'Hijo Número': 'ds_sonNumbr', 'Número de hermanos': 'ds_numbrBrothers',
                'Vive con': 'ds_livesWith', 'Teléfono Residencial Ficha': 'ds_residentialPhone',
                'Dirección Domicilio Ficha': 'ds_mainAddress', 'Nombre de la escuela': 'ds_schoolsName',
                'Curso Escolar': 'ds_schoolGrade', 'idInstitution': 'ds_idInstitution', 'idLevel': 'ds_idLevel'
            },
            'detail_fields': { # Campos a mostrar en la vista de detalle
                'Primer Nombre Catequizado': 'Nombre Catequizado', 'Primer Apellido Catequizado': 'Apellido Catequizado',
                'Nacimiento Catequizado': 'Fecha de Nacimiento', 'Sexo Catequizado': 'Sexo',
                'Dirección Domicilio Ficha': 'Dirección', 'Teléfono Residencial Ficha': 'Teléfono Fijo',
                'Nombre de la escuela': 'Escuela', 'Curso Escolar': 'Grado',
                'Primer Nombre Parent': 'Nombre del Padre', 'Ocupación Parent': 'Ocupación del Padre', 'Teléfono Parent': 'Contacto del Padre',
                'Primer Nombre Madre': 'Nombre de la Madre', 'Ocupación Madre': 'Ocupación de la Madre', 'Teléfono Madre': 'Contacto de la Madre',
                'Contacto de emergencia': 'Contacto de Emergencia', 'Teléfono de contacto de emergencia': 'Teléfono de Emergencia'
            }
        },
        'Payment': {
            'form': PaymentForm, 'sp_insert': 'sp_InsertPayment', 'sp_update': 'sp_UpdatePayment',
            'sp_delete': 'sp_DeletePayment', 'view': 'v_InfoPayment',
            'list_headers': ['ID', 'Nombre Catequizado', 'Monto', 'Fecha Pago', 'Estado'],
            'output_param': 'CreatedPaymentID', 'id_param': 'idPayment',
            
            # --- CAMBIO AQUÍ ---
            'field_map': {'ID': 'idPayment', 'Monto': 'amount', 'Metodo': 'paymentMethod', 'Fecha Pago': 'paymentDate', 'Estado': 'paymentState', 'idCatequizado': 'idCatequizado'},
            
            # --- Y CAMBIO AQUÍ ---
            # (La etiqueta para el usuario sí puede llevar acento)
            'detail_fields': {'ID': 'ID de Pago', 'Nombre Catequizado': 'Pagado por', 'Apellido Catequizado': '', 'Monto': 'Monto', 'Fecha Pago': 'Fecha', 'Metodo': 'Método de Pago', 'Estado': 'Estado del Pago'}
        },
        'Attendance': {
            'form': AttendanceForm, 'sp_insert': 'sp_InsertAttendance', 'sp_update': 'sp_UpdateAttendance',
            'sp_delete': 'sp_DeleteAttendance', 'view': 'v_InfoAttendance',
            'list_headers': ['Catequizado', 'Nivel', 'Fecha Registro', 'Estado Asistencia'],
            'id_param': ['idCurso', 'idCatequizado', 'dateOfAttendance'],
            'field_map': {'idCurso': 'idCurso', 'idCatequizado': 'idCatequizado', 'dateOfAttendance': 'dateOfAttendance', 'Estado Asistencia': 'state'},
            'detail_fields': {'Catequizado': 'Catequizado', 'Nivel': 'Nivel', 'Fecha Registro': 'Fecha', 'Estado Asistencia': 'Asistencia'}
        },
        'Acreditation': {
            'form': AcreditationForm, 'sp_insert': 'sp_InsertAcreditation', 'sp_update': 'sp_UpdateAcreditation',
            'sp_delete': 'sp_DeleteAcreditation', 'view': 'v_InfoAcreditation',
            'list_headers': ['ID', 'Catequizado', 'Institución'], 'output_param': 'CreatedAcreditationID', 'id_param': 'idAcreditation',
            'field_map': {'ID': 'idAcreditation', 'idInstitution': 'idInstitution', 'idCatequizado': 'idCatequizado', 'Contenido Acreditación': 'messageText'},
            'detail_fields': {'ID': 'ID Acreditación', 'Catequizado': 'Acreditado', 'Institución': 'Emitida por', 'Contenido Acreditación': 'Mensaje'}
        },
        'BautismFaith': {
            'form': BautismFaithForm, 'sp_insert': 'sp_InsertBautismFaith', 'sp_update': 'sp_UpdateBautismFaith',
            'sp_delete': 'sp_DeleteBautismFaith', 'view': 'v_InfoBauthismFaith',
            'list_headers': ['ID', 'Parroquia', 'Fecha Bautismo'], 'output_param': 'CreatedBautismFaithID', 'id_param': 'idBautismFaith',
            'field_map': {'ID': 'idBautismFaith', 'idCatequizado': 'idCatequizado', 'idParroquia': 'idParroquia', 'Fecha Bautismo': 'bautismDate', 'Registro Parroquial': 'numbrParroquialRegistration', 'idPadre': 'idPadre', 'idMadre': 'idMadre', 'idPadrino': 'idPadrino', 'Nota Marginal': 'marginalNote'},
            'detail_fields': {'ID': 'ID Fe de Bautismo', 'ID Catequizado': 'Catequizado (ID)', 'Parroquia': 'Parroquia', 'Fecha Bautismo': 'Fecha', 'Registro Parroquial': 'Nº Registro', 'Sacerdote': 'Sacerdote'}
        },
            'LevelAprobation': {
            'form': LevelAprobationForm, 'sp_insert': 'sp_InsertLevelAprobation', 'sp_update': 'sp_UpdateLevelAprobation',
            'sp_delete': 'sp_DeleteLevelAprobation', 'view': 'v_InfoLevelAprobation',
            'list_headers': ['ID', 'Catequizado', 'Nivel', 'Resultado'], 'output_param': 'CreatedLevelAprobationID', 'id_param': 'idLevelAprobation',
            'field_map': {'ID': 'idLevelAprobation', 'idCurso': 'idCurso', 'idCatequizado': 'idCatequizado', 'idCatequista': 'idCatequista', 'Resultado': 'resultOfLevel', 'Comentarios': 'commentaries'},
            'detail_fields': {'ID': 'idLevelAprobation', 'idCurso': 'idCurso', 'idCatequizado': 'idCatequizado', 'idCatequista': 'idCatequista', 'Resultado': 'Resultado', 'Comentarios': 'Comentarios'}
            },
            'LevelCertificate': {
            'form': LevelCertificateForm, 'sp_insert': 'sp_InsertLevelCertificate', 'sp_update': 'sp_UpdateLevelCertificate',
            'sp_delete': 'sp_DeleteLevelCertificate', 'view': 'v_InfoLevelCertificate',
            'list_headers': ['ID', 'Nivel', 'Fecha Entrega'], 'output_param': 'CreatedLevelCertificateID', 'id_param': 'idLevelCertificate',
            'field_map': {'ID': 'idLevelCertificate', 'idCurso': 'idCurso', 'idCatequizado': 'idCatequizado', 'idCatequista': 'idCatequista', 'idEclesiastico': 'idEclesiastico', 'Fecha Entrega': 'deliveryDate', 'Frase de Catequesis': 'catequesisPrhase', 'URL del Logo de la Parroquia': 'parroquiaLogo', 'Observaciones': 'commentaries'},
            'detail_fields': {'ID': 'ID', 'idCurso': 'Curso (Id)', 'idCatequizado': 'Catequizado', 'idCatequista': 'Catequista', 'idEclesiastico': 'Eclesiastico', 'Fecha Entrega': 'Fecha de Entrega', 'Frase de Catequesis': 'Frase de Catequesis', 'URL del Logo de la Parroquia': 'Parroquia Logo', 'Observaciones': 'Observaciones'}
            }
    }
    return roles.get(role)

def load_document_dynamic_choices(form, role, session):
    """Carga los menús desplegables para TODOS los formularios de documentos."""
    catequizados = None
    parroquias = None
    cursos = None
    
    # ---#-!-# LÍNEA CORREGIDA ---
    # Añadimos 'Attendance' a la lista de roles que necesitan cargar catequizados.
    if role in ['Payment', 'Acreditation', 'BautismFaith', 'LevelAprobation', 'LevelCertificate', 'Attendance']:
        catequizados = session.execute(text("SELECT ID, [Primer Nombre], [Primer Apellido] FROM Persons.v_InfoCatequizado WHERE Estado=1 ORDER BY [Primer Apellido]")).mappings().all()

    if role in ['Acreditation', 'BautismFaith']:
        parroquias = session.execute(text("SELECT [ID Institución], [Nombre Parroquia] FROM Institutions.v_InfoParroquia ORDER BY [Nombre Parroquia]")).mappings().all()

    if role in ['Attendance', 'LevelAprobation', 'LevelCertificate']:
        cursos = session.execute(text("SELECT ID, [Nombre Nivel], [Año del Período] FROM Nivel.v_InfoCurso ORDER BY [Año del Período] DESC")).mappings().all()

    # Asignar a los formularios
    if role == 'DataSheet':
        # La lógica de DataSheet ya era independiente y está bien.
        parroquias_ds = session.execute(text("SELECT [ID Institución], [Nombre Parroquia] FROM Institutions.v_InfoParroquia")).mappings().all()
        niveles_ds = session.execute(text("SELECT ID, Nombre FROM Nivel.v_InfoLevel")).mappings().all()
        form.c_idInstitution.choices = [('', '-- Opcional --')] + [(p['ID Institución'], p['Nombre Parroquia']) for p in parroquias_ds]
        form.ds_idInstitution.choices = [(p['ID Institución'], p['Nombre Parroquia']) for p in parroquias_ds]
        form.ds_idLevel.choices = [(n.ID, n.Nombre) for n in niveles_ds]

    elif role == 'Payment':
        form.idCatequizado.choices = [(c.ID, f"{c['Primer Nombre']} {c['Primer Apellido']}") for c in catequizados]
        
    elif role == 'Attendance':
        form.idCurso.choices = [(c.ID, f"{c['Nombre Nivel']} ({c['Año del Período']})") for c in cursos]
        # Ahora 'catequizados' no será None y este bucle funcionará
        form.idCatequizado.choices = [(c.ID, f"{c['Primer Nombre']} {c['Primer Apellido']}") for c in catequizados]

    elif role == 'Acreditation':
        form.idInstitution.choices = [(p['ID Institución'], p['Nombre Parroquia']) for p in parroquias]
        form.idCatequizado.choices = [(c.ID, f"{c['Primer Nombre']} {c['Primer Apellido']}") for c in catequizados]

    elif role == 'BautismFaith':
        parents = session.execute(text("SELECT ID, [Primer Nombre], [Primer Apellido] FROM Persons.v_InfoParent ORDER BY [Primer Apellido]")).mappings().all()
        padrinos = session.execute(text("SELECT ID, [Primer Nombre], [Primer Apellido] FROM Persons.v_InfoPadrino ORDER BY [Primer Apellido]")).mappings().all()
        form.idCatequizado.choices = [(c.ID, f"{c['Primer Nombre']} {c['Primer Apellido']}") for c in catequizados]
        form.idParroquia.choices = [(p['ID Institución'], p['Nombre Parroquia']) for p in parroquias]
        form.idPadre.choices = [('', '-- Opcional --')] + [(p.ID, f"{p['Primer Nombre']} {p['Primer Apellido']}") for p in parents]
        form.idMadre.choices = [('', '-- Opcional --')] + [(p.ID, f"{p['Primer Nombre']} {p['Primer Apellido']}") for p in parents]
        form.idPadrino.choices = [('', '-- Opcional --')] + [(p.ID, f"{p['Primer Nombre']} {p['Primer Apellido']}") for p in padrinos]

    elif role == 'LevelAprobation':
        catequistas = session.execute(text("SELECT ID, [Primer Nombre], [Primer Apellido] FROM Persons.v_InfoCatequista WHERE Estado=1")).mappings().all()
        form.idCurso.choices = [(c.ID, f"{c['Nombre Nivel']} ({c['Año del Período']})") for c in cursos]
        form.idCatequizado.choices = [(c.ID, f"{c['Primer Nombre']} {c['Primer Apellido']}") for c in catequizados]
        form.idCatequista.choices = [(c.ID, f"{c['Primer Nombre']} {c['Primer Apellido']}") for c in catequistas]

    elif role == 'LevelCertificate':
        catequistas = session.execute(text("SELECT ID, [Primer Nombre], [Primer Apellido] FROM Persons.v_InfoCatequista WHERE Estado=1")).mappings().all()
        eclesiasticos = session.execute(text("SELECT ID, [Primer Nombre], [Primer Apellido] FROM Persons.v_InfoEclesiastico WHERE Estado=1")).mappings().all()
        form.idCurso.choices = [(c.ID, f"{c['Nombre Nivel']} ({c['Año del Período']})") for c in cursos]
        form.idCatequizado.choices = [(c.ID, f"{c['Primer Nombre']} {c['Primer Apellido']}") for c in catequizados]
        form.idCatequista.choices = [(c.ID, f"{c['Primer Nombre']} {c['Primer Apellido']}") for c in catequistas]
        form.idEclesiastico.choices = [(e.ID, f"{e['Primer Nombre']} {e['Primer Apellido']}") for e in eclesiasticos]

@bp.route('/', methods=['GET', 'POST'])
def index():
    form = DocumentRolSelectorForm()
    if form.validate_on_submit():
        return redirect(url_for('Documents.list_items', role=form.role.data))
    return render_template('Documents/select_role.html', form=form, title="Gestionar Documentos")

@bp.route('/list/<role>')
def list_items(role):
    role_details = get_item_details(role)
    if not role_details:
        abort(404)
        
    SessionLocal = current_app.SessionLocal
    session = SessionLocal()
    try:
        stmt = text(f"SELECT * FROM Documents.{role_details['view']}")
        
        # --- LÍNEA CORREGIDA ---
        # Se elimina el segundo argumento `{}` cuando no hay parámetros.
        results = session.execute(stmt).mappings().all()

    finally:
        session.close()
        
    return render_template('Documents/list.html', 
                           items=results, 
                           headers=role_details['list_headers'], 
                           role=role, 
                           delete_form=DeleteForm(), 
                           title=f"Lista de {role}s")

@bp.route('/new/<role>', methods=['GET', 'POST'])
def new_item(role):
    role_details = get_item_details(role)
    if not role_details: abort(404)
    form = role_details['form']()
    SessionLocal = current_app.SessionLocal
    session = SessionLocal()
    try:
        load_document_dynamic_choices(form, role, session)
    finally:
        session.close()

    if form.validate_on_submit():
        params = {k: v for k, v in form.data.items() if k not in ['submit', 'csrf_token'] and v not in [None, '']}
        session = SessionLocal()
        try:
            placeholders = [f"@{k}=:{k}" for k in params.keys()]
            if 'output_param' in role_details:
                output_param = role_details['output_param']
                sql = f"""
                    DECLARE @{output_param} INT;
                    EXEC Documents.{role_details['sp_insert']} {', '.join(placeholders)}, @{output_param}=@{output_param} OUTPUT;
                    SELECT @{output_param};
                """
                created_id = session.execute(text(sql), params).scalar_one()
                flash(f'{role} creado con ID: {created_id}.', 'success')
            else:
                sql = f"EXEC Documents.{role_details['sp_insert']} {', '.join(placeholders)}"
                session.execute(text(sql), params)
                flash(f'{role} registrado exitosamente.', 'success')
            
            session.commit()
            return redirect(url_for('Documents.list_items', role=role))
        except exc.SQLAlchemyError as e:
            if session.is_active: session.rollback()
            flash(f"Error al crear {role}: {getattr(e, 'orig', e)}", 'danger')
        finally:
            session.close()
    
    field_groups = {}
    if role == 'DataSheet':
        field_groups = {
            'Datos del Catequizado': [f for f in form if f.name.startswith('c_')],
            'Datos del Padre': [f for f in form if f.name.startswith('f_')],
            'Datos de la Madre': [f for f in form if f.name.startswith('m_')],
            'Información de la Ficha': [f for f in form if f.name.startswith('ds_')]
        }

    return render_template('Documents/form.html', form=form, title=f'Nuevo {role}', role=role, action_url=url_for('Documents.new_item', role=role), field_groups=field_groups)


@bp.route('/edit/<role>/<int:item_id>', methods=['GET', 'POST'])
def edit_item(role, item_id):
    role_details = get_item_details(role)
    if not role_details: abort(404)


    # Redirigir entidades complejas a sus rutas específicas
    if role == 'Attendance':
        flash('La edición para Asistencia tiene una ruta especial.', 'info')
        return redirect(url_for('Documents.list_items', role=role))
    if role == 'DataSheet':
        return redirect(url_for('Documents.edit_datasheet', item_id=item_id))

    RoleForm = role_details['form']
    SessionLocal = current_app.SessionLocal
    session = SessionLocal()
    
    try:
        id_column_name = role_details['list_headers'][0]
        # Asegúrate que las vistas tengan todas las columnas de ID necesarias para el field_map
        query = text(f"SELECT * FROM Documents.{role_details['view']} WHERE \"{id_column_name}\" = :id")
        item_data_from_view = session.execute(query, {"id": item_id}).mappings().fetchone()

        if not item_data_from_view:
            flash(f"{role} con ID {item_id} no encontrado.", 'warning')
            return redirect(url_for('Documents.list_items', role=role))

        form_data = {}
        field_map = role_details.get('field_map', {})
        for view_key, form_key in field_map.items():
            if view_key in item_data_from_view:
                form_data[form_key] = item_data_from_view[view_key]
        
        form = RoleForm(data=form_data) if request.method == 'GET' else RoleForm()
        load_document_dynamic_choices(form, role, session)

        if form.validate_on_submit():
            params = {k: v for k, v in form.data.items() if k not in ['submit', 'csrf_token']}
            params[role_details['id_param']] = item_id
            
            placeholders = [f"@{k}=:{k}" for k in params.keys()]
            sql_string = f"EXEC Documents.{role_details['sp_update']} {', '.join(placeholders)}"

            session.execute(text(sql_string), params)
            session.commit()
            flash(f"{role} actualizado exitosamente.", 'success')
            return redirect(url_for('Documents.list_items', role=role))

        return render_template('Documents/form.html', form=form, title=f'Editar {role}', role=role, action_url=url_for('Documents.edit_item', role=role, item_id=item_id))
    finally:
        session.close()

@bp.route('/edit/Attendance/<int:curso_id>/<int:catequizado_id>/<string:date_str>', methods=['GET', 'POST'])
def edit_attendance(curso_id, catequizado_id, date_str):
    role = 'Attendance'
    role_details = get_item_details(role)
    RoleForm = role_details['form']
    
    SessionLocal = current_app.SessionLocal
    session = SessionLocal()
    try:
        item_data = session.execute(
            text("SELECT * FROM Documents.v_InfoAttendance WHERE idCurso = :cid AND idCatequizado = :catid AND dateOfAttendance = :date"),
            {"cid": curso_id, "catid": catequizado_id, "date": date_str}
        ).mappings().fetchone()

        if not item_data:
            flash("Registro de asistencia no encontrado.", 'warning')
            return redirect(url_for('Documents.list_items', role=role))

        form_data = {form_key: item_data[view_key] for view_key, form_key in role_details['field_map'].items() if view_key in item_data}
        form = RoleForm(data=form_data) if request.method == 'GET' else RoleForm()

        form.idCurso.render_kw = {'disabled': 'disabled'}
        form.idCatequizado.render_kw = {'disabled': 'disabled'}
        form.dateOfAttendance.render_kw = {'disabled': 'disabled'}
        load_document_dynamic_choices(form, role, session)

        if form.validate_on_submit():
            params = {
                'idCurso': curso_id, 'idCatequizado': catequizado_id,
                'dateOfAttendance': date_str, 'state': form.state.data
            }
            sql = text("EXEC Documents.sp_UpdateAttendance @idCurso=:idCurso, @idCatequizado=:idCatequizado, @dateOfAttendance=:dateOfAttendance, @state=:state")
            session.execute(sql, params)
            session.commit()
            flash('Asistencia actualizada.', 'success')
            return redirect(url_for('Documents.list_items', role=role))

        return render_template('Documents/form.html', form=form, title='Editar Asistencia', role=role, action_url=url_for('Documents.edit_attendance', curso_id=curso_id, catequizado_id=catequizado_id, date_str=date_str))
    finally:
        session.close()


# Las rutas de borrado y detalle que tenías antes están bien.
@bp.route('/delete/<role>', methods=['POST'])
def delete_item(role):
    role_details = get_item_details(role)
    if not role_details: abort(404)
    if not DeleteForm().validate_on_submit():
        return redirect(url_for('Documents.list_items', role=role))
    
    SessionLocal = current_app.SessionLocal
    session = SessionLocal()
    try:
        id_params = role_details['id_param']
        if isinstance(id_params, list):
            params = {key: request.form.get(key) for key in id_params}
            placeholders = [f"@{k}=:{k}" for k in params.keys()]
            sql = text(f"EXEC Documents.{role_details['sp_delete']} {', '.join(placeholders)}")
            session.execute(sql, params)
        else:
            item_id = request.form.get('item_id')
            sql = text(f"EXEC Documents.{role_details['sp_delete']} @{id_params} = :id")
            session.execute(sql, {"id": item_id})
        
        session.commit()
        flash(f'{role} ha sido eliminado.', 'success')
    except exc.SQLAlchemyError as e:
        session.rollback()
        flash(f"Error al eliminar {role}: {getattr(e, 'orig', e)}", 'danger')
    finally:
        session.close()
    return redirect(url_for('Documents.list_items', role=role))

@bp.route('/<role>/<int:item_id>')
def detail_item(role, item_id):
    role_details = get_item_details(role)
    if not role_details: abort(404)
    if role == 'Attendance':
        flash('La vista de detalle para Asistencia no es necesaria.', 'info')
        return redirect(url_for('Documents.list_items', role=role))
        
    SessionLocal = current_app.SessionLocal
    session = SessionLocal()
    detail_items = []
    
    try:
        id_column_name = role_details['list_headers'][0]
        query = text(f"SELECT * FROM Documents.{role_details['view']} WHERE \"{id_column_name}\" = :id")
        item_data = session.execute(query, {"id": item_id}).mappings().fetchone()

        if not item_data:
            flash(f"Registro de {role} no encontrado.", 'warning')
            return redirect(url_for('Documents.list_items', role=role))
        
        detail_fields = role_details.get('detail_fields', {})
        for column_name, label in detail_fields.items():
            if column_name in item_data:
                value = item_data[column_name]
                if isinstance(value, bool):
                    value = 'Sí' if value else 'No'
                elif isinstance(value, datetime.date):
                    value = value.strftime('%d-%m-%Y')
                
                # Para combinar nombre y apellido en el detalle
                if label: # Si la etiqueta no está vacía
                    detail_items.append((label, value if value is not None else 'N/A'))
            
    finally:
        session.close()

    if not detail_items:
        flash("No hay detalles configurados para este tipo de documento.", "warning")
        return redirect(url_for('Documents.list_items', role=role))

    return render_template('Documents/detail.html', detail_items=detail_items, title=f"Detalle de {role}", role=role)

@bp.route('/edit/DataSheet/<int:item_id>', methods=['GET', 'POST'])
def edit_datasheet(item_id):
    role = 'DataSheet'
    role_details = get_item_details(role)
    if not role_details: abort(404)

    RoleForm = role_details['form']
    SessionLocal = current_app.SessionLocal
    session = SessionLocal()
    
    try:
        query = text(f"SELECT * FROM Documents.{role_details['view']} WHERE idDataSheet = :id")
        item_data_from_view = session.execute(query, {"id": item_id}).mappings().fetchone()

        if not item_data_from_view:
            flash("Ficha de Datos no encontrada.", 'warning')
            return redirect(url_for('Documents.list_items', role=role))

        form_data = {}
        field_map = role_details.get('field_map', {})
        for view_key, form_key in field_map.items():
            if view_key in item_data_from_view:
                form_data[form_key] = item_data_from_view[view_key]
        
        # El formulario se instancia con los datos ya transformados si es un GET.
        form = RoleForm(data=form_data) if request.method == 'GET' else RoleForm()
        
        load_document_dynamic_choices(form, role, session)

        if form.validate_on_submit():
            params = {k: v for k, v in form.data.items() if k not in ['submit', 'csrf_token']}
            params[role_details['id_param']] = item_id
            
            placeholders = [f"@{k}=:{k}" for k in params.keys()]
            sql_string = f"EXEC Documents.{role_details['sp_update']} {', '.join(placeholders)}"

            session.execute(text(sql_string), params)
            session.commit()
            flash("Ficha de Datos actualizada exitosamente.", 'success')
            return redirect(url_for('Documents.list_items', role=role))
        
        field_groups = {
            'Datos del Catequizado': [f for f in form if f.name.startswith('c_')],
            'Datos del Padre': [f for f in form if f.name.startswith('f_')],
            'Datos de la Madre': [f for f in form if f.name.startswith('m_')],
            'Información de la Ficha': [f for f in form if f.name.startswith('ds_')]
        }

        return render_template(
            'Documents/form.html',
            form=form,
            title=f'Editar Ficha de Datos (ID: {item_id})',
            role=role,
            action_url=url_for('Documents.edit_datasheet', item_id=item_id),
            field_groups=field_groups
        )
    finally:
        session.close()

@bp.route('/DataSheet/<int:item_id>')
def detail_datasheet(item_id):
    role = 'DataSheet'
    role_details = get_item_details(role)
    if not role_details: abort(404)
        
    SessionLocal = current_app.SessionLocal
    session = SessionLocal()
    detail_items = []
    
    try:
        query = text(f"SELECT * FROM Documents.{role_details['view']} WHERE idDataSheet = :id")
        item_data = session.execute(query, {"id": item_id}).mappings().fetchone()

        if not item_data:
            return redirect(url_for('Documents.list_items', role=role))
        
        detail_fields = role_details.get('detail_fields', {})
        for column_name, label in detail_fields.items():
            if column_name in item_data:
                value = item_data[column_name]
                if isinstance(value, datetime.date):
                    value = value.strftime('%d-%m-%Y')
                detail_items.append((label, value if value is not None else 'N/A'))
            
    finally:
        session.close()

    return render_template('Documents/detail.html', detail_items=detail_items, title=f"Detalle de Ficha (ID: {item_id})", role=role)