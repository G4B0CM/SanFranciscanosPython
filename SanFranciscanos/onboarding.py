# backend/onboarding.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from sqlalchemy import text, exc
from .forms import DataSheetForm, BautismFaithFormHidden, PaymentFormHidden, OnboardingEnrollmentForm
from .documents import load_document_dynamic_choices # Reutilizamos la lógica de carga

bp = Blueprint('Onboarding', __name__, url_prefix='/Onboarding')


# --- PASO 1: FICHA DE DATOS ---

@bp.route('/start')
def start():
    """Paso 1: Muestra el formulario para la Ficha de Datos."""
    form = DataSheetForm()
    SessionLocal = current_app.SessionLocal
    session = SessionLocal()
    try:
        load_document_dynamic_choices(form, 'DataSheet', session)
    finally:
        session.close()

    # ---#-!-# LÓGICA DE PYTHON: PREPARAR LOS DATOS AQUÍ ---
    field_groups = {
        'Datos del Catequizado': [f for f in form if f.name.startswith('c_')],
        'Datos del Padre (Opcional)': [f for f in form if f.name.startswith('f_')],
        'Datos de la Madre (Opcional)': [f for f in form if f.name.startswith('m_')],
        'Información Escolar y Familiar': [f for f in form if f.name.startswith('ds_')]
    }

    return render_template('Onboarding/step_form.html',
                           form=form,
                           title="Paso 1 de 4: Ficha de Inscripción",
                           step=1,
                           action_url=url_for('Onboarding.process_datasheet'),
                           field_groups=field_groups)


@bp.route('/process_datasheet', methods=['POST'])
def process_datasheet():
    """Procesa la Ficha de Datos y redirige al siguiente paso."""
    form = DataSheetForm()
    
    # ---#-!-# DEPURACIÓN: Imprimir datos recibidos del formulario ---
    print("--- Datos Recibidos del Formulario ---")
    print(request.form)
    print("--------------------------------------")
    
    SessionLocal = current_app.SessionLocal
    session = SessionLocal()
    try:
        load_document_dynamic_choices(form, 'DataSheet', session)
    finally:
        session.close()

    if form.validate_on_submit():
        print("--- El formulario es VÁLIDO. Intentando inserción en BD... ---")
        params = {k: v for k, v in form.data.items() if k not in ['submit', 'csrf_token'] and v not in [None, '']}
        
        # El SP necesita 'c_state' aunque sea un checkbox no marcado
        if 'c_state' not in params:
            params['c_state'] = False
        
        session = SessionLocal()
        try:
            placeholders = [f"@{k}=:{k}" for k in params.keys()]
            # Asegurarse de que todos los parámetros del SP estén en la llamada
            sql = f"""
                DECLARE @CreatedDataSheetID INT;
                EXEC Documents.sp_InsertDataSheet {', '.join(placeholders)}, @CreatedDataSheetID=@CreatedDataSheetID OUTPUT;
                SELECT @CreatedDataSheetID;
            """
            
            # ---#-!-# DEPURACIÓN: Imprimir la consulta SQL y los parámetros ---
            print("--- Ejecutando SQL ---")
            print(sql)
            print("--- Con Parámetros ---")
            print(params)
            print("----------------------")
            
            created_datasheet_id = session.execute(text(sql), params).scalar_one()

            if created_datasheet_id is None:
                # El SP no devolvió un ID, algo salió mal silenciosamente
                raise Exception("La creación de la ficha de datos no devolvió un ID.")

            catequizado_id = session.execute(text("SELECT idCatequizado FROM Documents.DataSheet WHERE idDataSheet = :id"), {"id": created_datasheet_id}).scalar_one()
            session.commit()
            
            flash('Paso 1 completado: Ficha de Datos creada.', 'success')
            return redirect(url_for('Onboarding.step_bautism', catequizado_id=catequizado_id))

        except exc.SQLAlchemyError as e:
            if session.is_active: session.rollback()
            error_msg = f"Error de Base de Datos en el Paso 1: {getattr(e, 'orig', e)}"
            print(f"!!! ERROR DE BD: {error_msg} !!!")
            flash(error_msg, 'danger')
        except Exception as e:
            error_msg = f"Error Inesperado en el Paso 1: {e}"
            print(f"!!! ERROR INESPERADO: {error_msg} !!!")
            flash(error_msg, 'danger')
        finally:
            if session.is_active:
                session.close()
    else:
        # ---#-!-# DEPURACIÓN: Imprimir errores de validación ---
        print("--- El formulario NO es válido. Errores: ---")
        print(form.errors)
        print("------------------------------------------")
        flash('El formulario contiene errores. Por favor, revíselos.', 'warning')

    # Si llegamos aquí, es porque algo falló. Re-renderizamos el formulario.
    field_groups = {
        'Datos del Catequizado': [f for f in form if f.name.startswith('c_')],
        'Datos del Padre (Opcional)': [f for f in form if f.name.startswith('f_')],
        'Datos de la Madre (Opcional)': [f for f in form if f.name.startswith('m_')],
        'Información Escolar y Familiar': [f for f in form if f.name.startswith('ds_')]
    }
    return render_template('Onboarding/step_form.html',
                           form=form,
                           title="Paso 1 de 4: Ficha de Inscripción (Corregir Errores)",
                           step=1,
                           action_url=url_for('Onboarding.process_datasheet'),
                           field_groups=field_groups)


# --- PASO 2: FE DE BAUTISMO ---

@bp.route('/step/bautism/<int:catequizado_id>')
def step_bautism(catequizado_id):
    """Paso 2: Muestra el formulario para la Fe de Bautismo."""
    form = BautismFaithFormHidden(data={'idCatequizado': catequizado_id})
    SessionLocal = current_app.SessionLocal
    session = SessionLocal()
    try:
        # Pre-poblar los dropdowns para la primera carga
        load_document_dynamic_choices(form, 'BautismFaith', session)
    finally:
        session.close()
    
    return render_template('Onboarding/step_form.html',
                           form=form,
                           title="Paso 2 de 4: Fe de Bautismo",
                           step=2,
                           action_url=url_for('Onboarding.process_bautism', catequizado_id=catequizado_id),
                           catequizado_id=catequizado_id)


@bp.route('/process/bautism/<int:catequizado_id>', methods=['POST'])
def process_bautism(catequizado_id):
    """Procesa la Fe de Bautismo."""
    form = BautismFaithFormHidden()
    # Forzamos el ID del catequizado, ya que no debe ser editable en este paso.
    form.idCatequizado.data = catequizado_id
    
    SessionLocal = current_app.SessionLocal
    session = SessionLocal()
    try:
        # Es crucial volver a cargar los choices para que, si hay un error de validación,
        # los dropdowns no aparezcan vacíos al recargar la página.
        load_document_dynamic_choices(form, 'BautismFaith', session)
    finally:
        session.close()

    if form.validate_on_submit():
        print("--- Formulario de Bautismo VÁLIDO. Intentando inserción... ---")
        params = {k: v for k, v in form.data.items() if k not in ['submit', 'csrf_token'] and v not in [None, '']}
        session = SessionLocal()
        try:
            placeholders = [f"@{k}=:{k}" for k in params.keys()]
            sql = f"""
                DECLARE @CreatedBautismFaithID INT;
                EXEC Documents.sp_InsertBautismFaith {', '.join(placeholders)}, @CreatedBautismFaithID=@CreatedBautismFaithID OUTPUT;
                SELECT @CreatedBautismFaithID;
            """
            result = session.execute(text(sql), params).scalar_one()
            if result is None:
                raise Exception("El SP de Fe de Bautismo no devolvió un ID.")

            session.commit()
            flash('Paso 2 completado: Fe de Bautismo registrada.', 'success')
            return redirect(url_for('Onboarding.step_payment', catequizado_id=catequizado_id))
        except exc.SQLAlchemyError as e:
            if session.is_active: session.rollback()
            error_msg = f"Error de Base de Datos en el Paso 2: {getattr(e, 'orig', e)}"
            print(f"!!! ERROR DE BD: {error_msg} !!!")
            flash(error_msg, 'danger')
        except Exception as e:
            error_msg = f"Error Inesperado en el Paso 2: {e}"
            print(f"!!! ERROR INESPERADO: {error_msg} !!!")
            flash(error_msg, 'danger')
        finally:
            if session.is_active: session.close()
    else:
        print("--- Formulario de Bautismo NO válido. Errores: ---")
        print(form.errors)
        print("-------------------------------------------------")
        flash('El formulario contiene errores. Por favor, revíselos.', 'warning')

    return render_template('Onboarding/step_form.html',
                           form=form,
                           title="Paso 2 de 4: Fe de Bautismo (Corregir Errores)",
                           step=2,
                           action_url=url_for('Onboarding.process_bautism', catequizado_id=catequizado_id),
                           catequizado_id=catequizado_id)


# --- PASO 3: PAGO ---

@bp.route('/step/payment/<int:catequizado_id>')
def step_payment(catequizado_id):
    """Paso 3: Muestra el formulario de Pago."""
    form = PaymentFormHidden(data={'idCatequizado': catequizado_id})
    return render_template('Onboarding/step_form.html',
                           form=form,
                           title="Paso 3 de 4: Registrar Pago",
                           step=3,
                           action_url=url_for('Onboarding.process_payment', catequizado_id=catequizado_id),
                           catequizado_id=catequizado_id)


@bp.route('/process/payment/<int:catequizado_id>', methods=['POST'])
def process_payment(catequizado_id):
    """Procesa el Pago."""
    form = PaymentFormHidden()
    form.idCatequizado.data = catequizado_id
    SessionLocal = current_app.SessionLocal
    session = SessionLocal()
    # El formulario de pago no tiene dropdowns, pero el patrón de validación es el mismo.
    if form.validate_on_submit():
        print("--- Formulario de Pago VÁLIDO. Intentando inserción... ---")
        params = {k: v for k, v in form.data.items() if k not in ['submit', 'csrf_token'] and v not in [None, '']}
        session = SessionLocal()
        try:
            placeholders = [f"@{k}=:{k}" for k in params.keys()]
            sql = f"""
                DECLARE @CreatedPaymentID INT;
                EXEC Documents.sp_InsertPayment {', '.join(placeholders)}, @CreatedPaymentID=@CreatedPaymentID OUTPUT;
                SELECT @CreatedPaymentID;
            """
            result = session.execute(text(sql), params).scalar_one()
            if result is None:
                raise Exception("El SP de Pago no devolvió un ID.")
            
            session.commit()
            flash('Paso 3 completado: Pago registrado.', 'success')
            return redirect(url_for('Onboarding.step_enrollment', catequizado_id=catequizado_id))
        except exc.SQLAlchemyError as e:
            if session.is_active: session.rollback()
            error_msg = f"Error de Base de Datos en el Paso 3: {getattr(e, 'orig', e)}"
            print(f"!!! ERROR DE BD: {error_msg} !!!")
            flash(error_msg, 'danger')
        except Exception as e:
            error_msg = f"Error Inesperado en el Paso 3: {e}"
            print(f"!!! ERROR INESPERADO: {error_msg} !!!")
            flash(error_msg, 'danger')
        finally:
            if session.is_active: session.close()
    else:
        print("--- Formulario de Pago NO válido. Errores: ---")
        print(form.errors)
        print("---------------------------------------------")
        flash('El formulario contiene errores. Por favor, revíselos.', 'warning')
    
    return render_template('Onboarding/step_form.html',
                           form=form,
                           title="Paso 3 de 4: Registrar Pago (Corregir Errores)",
                           step=3,
                           action_url=url_for('Onboarding.process_payment', catequizado_id=catequizado_id),
                           catequizado_id=catequizado_id)


# --- PASO 4: INSCRIPCIÓN EN CURSO ---

@bp.route('/step/enrollment/<int:catequizado_id>')
def step_enrollment(catequizado_id):
    """Paso 4: Muestra el formulario para inscribir en un curso."""
    # Usamos el formulario correcto y simple
    form = OnboardingEnrollmentForm()
    SessionLocal = current_app.SessionLocal
    session = SessionLocal()
    try:
        cursos = session.execute(text("SELECT ID, [Nombre Nivel], [Año del Período] FROM Nivel.v_InfoCurso ORDER BY [Año del Período] DESC, [Nombre Nivel]")).mappings().all()
        form.idCurso.choices = [(c.ID, f"{c['Nombre Nivel']} ({c['Año del Período']})") for c in cursos]
    finally:
        session.close()
    
    return render_template('Onboarding/step_enrollment_form.html',
                           form=form,
                           title="Paso 4 de 4: Inscribir en un Curso",
                           step=4,
                           catequizado_id=catequizado_id)


@bp.route('/process/enrollment/<int:catequizado_id>', methods=['POST'])
def process_enrollment(catequizado_id):
    """Procesa la inscripción final usando un envío HTML tradicional."""
    
    # Usamos el mismo formulario para renderizar y para validar
    form = OnboardingEnrollmentForm()
    
    # Poblamos las opciones antes de validar
    SessionLocal = current_app.SessionLocal
    session = SessionLocal()
    try:
        cursos = session.execute(text("SELECT ID, [Nombre Nivel], [Año del Período] FROM Nivel.v_InfoCurso ORDER BY [Año del Período] DESC, [Nombre Nivel]")).mappings().all()
        form.idCurso.choices = [(c.ID, f"{c['Nombre Nivel']} ({c['Año del Período']})") for c in cursos]
    finally:
        session.close()

    if form.validate_on_submit():
        id_curso = form.idCurso.data
        session = SessionLocal()
        try:
            sp_sql = text("EXEC Nivel.sp_InsertGrupos @idCurso=:idCurso, @idCatequizado=:idCatequizado")
            session.execute(sp_sql, {"idCurso": id_curso, "idCatequizado": catequizado_id})
            session.commit()
            
            flash('¡Inscripción exitosa! El catequizado ha sido añadido al curso.', 'success')
            return redirect(url_for('Onboarding.finish'))

        except exc.SQLAlchemyError as e:
            # ... (la lógica de manejo de errores se mantiene igual) ...
            if session.is_active: session.rollback()
            raw_error_msg = str(getattr(e, 'orig', e))
            try:
                start_index = raw_error_msg.rfind('[SQL Server]') + len('[SQL Server]')
                end_index = raw_error_msg.rfind(' (50000)') if '(50000)' in raw_error_msg else -1
                clean_msg = raw_error_msg[start_index:end_index].strip() if start_index > -1 and end_index > start_index else raw_error_msg.split('] ')[-1]
            except:
                clean_msg = raw_error_msg
            
            flash(f'Error en la Inscripción: {clean_msg}', 'danger')
            return redirect(url_for('Onboarding.step_enrollment', catequizado_id=catequizado_id))
        finally:
            if session.is_active: session.close()
    else:
        # Si la validación falla, este mensaje ahora es correcto
        flash('Debe seleccionar un curso para continuar.', 'warning')
        return redirect(url_for('Onboarding.step_enrollment', catequizado_id=catequizado_id))


# --- PASO 5: FINALIZACIÓN ---

@bp.route('/finish')
def finish():
    """Muestra la pantalla de finalización del proceso."""
    return render_template('Onboarding/finish.html')