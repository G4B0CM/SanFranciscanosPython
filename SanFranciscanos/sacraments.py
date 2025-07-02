# Archivo: sacraments.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from sqlalchemy import text
from .forms import SacramentForm, DeleteForm
import datetime
from SanFranciscanos.db import SessionLocal  # Importar la sesión de la base de datos

bp = Blueprint('Sacraments', __name__, url_prefix='/Sacraments')

@bp.route('/')
def index():
    session = SessionLocal()
    try:
        sacraments = session.execute(text("SELECT * FROM Sacraments.vw_ListSacrament")).fetchall()
    except Exception as e:
        flash(f"Error al cargar los sacramentos: {str(e)}", 'danger')
        sacraments = []
    finally:
        session.close()

    delete_form = DeleteForm()
    return render_template('Sacraments/list_sacraments.html', sacraments=sacraments, delete_form=delete_form, title="Lista de Sacramentos")

@bp.route('/new', methods=['GET', 'POST'])
def new():
    form = SacramentForm()
    if form.validate_on_submit():
        params = {key: value for key, value in form.data.items() if key != 'submit'}
        params['createdAt'] = datetime.datetime.utcnow()
        params['updatedAt'] = datetime.datetime.utcnow()
        params['state'] = 'Activo'
        session = SessionLocal()
        try:
            sql = ("EXEC Sacraments.sp_InsertSacrament @name = :name, "
                   "@description = :description, @required = :required, "
                   "@createdAt = :createdAt, @updatedAt = :updatedAt, @state = :state")
            session.execute(text(sql), params)
            session.commit()
            flash("Sacramento creado exitosamente.", 'success')
            return redirect(url_for('Sacraments.index'))
        except Exception as e:
            session.rollback()
            flash(f"Error al crear el sacramento: {str(e)}", 'danger')
        finally:
            session.close()
    return render_template('Sacraments/sacrament_form.html', form=form, title="Nuevo Sacramento")

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    form = SacramentForm()
    session = SessionLocal()
    try:
        result = session.execute(text("SELECT * FROM Sacraments.vw_ListSacrament WHERE idSacrament = :id"), {"id": id}).fetchone()
        if not result:
            flash("Sacramento no encontrado.", 'warning')
            return redirect(url_for('Sacraments.index'))

        if request.method == 'GET':
            for field in form:
                if field.name in result.keys():
                    field.data = result[field.name]

        if form.validate_on_submit():
            params = {key: value for key, value in form.data.items() if key != 'submit'}
            params['id'] = id
            params['updatedAt'] = datetime.datetime.utcnow()
            sql = ("EXEC Sacraments.sp_UpdateSacrament @id = :id, @name = :name, "
                   "@description = :description, @required = :required, @updatedAt = :updatedAt")
            session.execute(text(sql), params)
            session.commit()
            flash("Sacramento actualizado exitosamente.", 'success')
            return redirect(url_for('Sacraments.index'))

    except Exception as e:
        session.rollback()
        flash(f"Error al editar el sacramento: {str(e)}", 'danger')
    finally:
        session.close()

    return render_template('Sacraments/sacrament_form.html', form=form, title="Editar Sacramento")

@bp.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    session = SessionLocal()
    try:
        sql = text("EXEC Sacraments.sp_DeleteSacrament @idSacramentToDelete = :id")
        session.execute(sql, {"id": id})
        session.commit()
        flash("Sacramento eliminado correctamente.", 'success')
    except Exception as e:
        session.rollback()
        flash(f"Error al eliminar el sacramento: {str(e)}", 'danger')
    finally:
        session.close()

    return redirect(url_for('Sacraments.index'))

@bp.route('/<int:sacrament_id>')
def detail(sacrament_id):
    session = SessionLocal()
    sacrament = session.execute(text("SELECT * FROM Sacraments.vw_ListSacrament WHERE idSacrament = :id"), {'id': sacrament_id}).fetchone()
    session.close()
    if not sacrament:
        flash("Sacramento no encontrado.", 'warning')
        return redirect(url_for('Sacraments.index'))
    return render_template('Sacraments/detail_sacrament.html', sacrament=sacrament, title="Detalle del Sacramento")
