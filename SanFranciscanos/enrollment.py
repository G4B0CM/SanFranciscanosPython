# backend/enrollments.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from sqlalchemy import text, exc
from .forms import EnrollmentForm

bp = Blueprint('Enrollments', __name__, url_prefix='/Enrollments')

@bp.route('/', methods=['GET', 'POST'])
def enroll():
    form = EnrollmentForm()
    SessionLocal = current_app.SessionLocal
    session = SessionLocal()
    
    try:
        # Cargar opciones para los dropdowns
        cursos = session.execute(text("SELECT ID, [Nombre Nivel], [Año del Período] FROM Nivel.v_InfoCurso ORDER BY [Año del Período] DESC, [Nombre Nivel]")).mappings().all()
        form.idCurso.choices = [(c.ID, f"{c['Nombre Nivel']} ({c['Año del Período']})") for c in cursos]

        catequizados = session.execute(text("SELECT ID, [Primer Nombre], [Primer Apellido] FROM Persons.v_InfoCatequizado WHERE Estado=1 ORDER BY [Primer Apellido]")).mappings().all()
        form.catequizados.choices = [(c.ID, f"{c['Primer Nombre']} {c['Primer Apellido']}") for c in catequizados]

    finally:
        session.close()

    if form.validate_on_submit():
        id_curso = form.idCurso.data
        ids_catequizados = form.catequizados.data
        
        success_count = 0
        error_messages = []

        session = SessionLocal()
        try:
            for catequizado_id in ids_catequizados:
                try:
                    sp_sql = text("EXEC Nivel.sp_InsertGrupos @idCurso=:idCurso, @idCatequizado=:idCatequizado")
                    session.execute(sp_sql, {"idCurso": id_curso, "idCatequizado": catequizado_id})
                    session.commit()
                    success_count += 1
                except exc.SQLAlchemyError as e:
                    session.rollback()
                    
                    # ---#-!-# LÓGICA DE LIMPIEZA DE ERRORES MEJORADA ---
                    raw_error_msg = str(getattr(e, 'orig', e))
                    
                    # Intentamos encontrar el mensaje útil que viene después de '[SQL Server]'
                    # y antes del código de error '(50000)'.
                    try:
                        # Buscamos el final del prefijo del driver
                        start_index = raw_error_msg.rfind('[SQL Server]') + len('[SQL Server]')
                        # Buscamos el inicio del código de error SQL
                        end_index = raw_error_msg.rfind(' (50000)')
                        
                        # Si encontramos ambos marcadores, extraemos el texto entre ellos
                        if start_index > -1 and end_index > start_index:
                            clean_msg = raw_error_msg[start_index:end_index].strip()
                        else:
                            # Si no, usamos un método de fallback más simple
                            clean_msg = raw_error_msg.split('] ')[-1]
                    except:
                        # Si todo falla, mostramos el error crudo pero limpio
                        clean_msg = raw_error_msg.replace("('42000', ", "").replace(")", "")
                    
                    error_messages.append(clean_msg)
            
            # Devolvemos una respuesta JSON para que el frontend la procese con el modal
            return jsonify({
                'success': True,
                'success_count': success_count,
                'error_messages': error_messages
            })

        finally:
            session.close()

    # Si es una petición GET, simplemente renderizamos la página.
    return render_template('Enrollments/enroll_form.html', form=form, title="Inscribir Catequizados en un Curso")


@bp.route('/list')
def list_enrollments():
    """Muestra la lista de inscripciones actuales."""
    SessionLocal = current_app.SessionLocal
    session = SessionLocal()
    try:
        results = session.execute(text("SELECT * FROM Nivel.v_InfoGrupos ORDER BY idCurso, [Nombre Catequizado]")).mappings().all()
    finally:
        session.close()
    
    return render_template('Enrollments/list.html', items=results, title="Lista de Inscripciones")