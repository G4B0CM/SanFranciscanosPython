from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from sqlalchemy import text
from .forms import LevelForm, DeleteForm
import datetime
from SanFranciscanos.db import SessionLocal  # Importar la sesión de la base de datos

bp = Blueprint('Levels', __name__, url_prefix='/Levels')

@bp.route('/')
def index():
    session = SessionLocal()
    try:
        levels = session.execute(text("SELECT * FROM Levels.vw_ListLevels")).fetchall()
    except Exception as e:
        flash(f"Error al obtener niveles: {str(e)}", 'danger')
        levels = []
    finally:
        session.close()

    delete_form = DeleteForm()
    return render_template('Levels/list_levels.html', levels=levels, delete_form=delete_form, title="Lista de Niveles")

@bp.route('/new', methods=['GET', 'POST'])
def create_level():
    form = LevelForm()
    if form.validate_on_submit():
        params = {
            key: value for key, value in form.data.items()
            if key != 'submit' and value != ''
        }
        params['createdAt'] = datetime.datetime.utcnow()
        params['updatedAt'] = datetime.datetime.utcnow()
        params['state'] = 'Activo'

        session = SessionLocal()
        try:
            sql = ("EXEC Levels.sp_InsertLevel "
                   "@name = :name, @description = :description, @order = :order, "
                   "@createdAt = :createdAt, @updatedAt = :updatedAt, @state = :state")
            session.execute(text(sql), params)
            session.commit()
            flash("Nivel creado exitosamente.", 'success')
            return redirect(url_for('Levels.index'))
        except Exception as e:
            session.rollback()
            flash(f"Error al crear nivel: {str(e)}", 'danger')
        finally:
            session.close()

    return render_template('Levels/level_form.html', form=form, title="Nuevo Nivel")

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_level(id):
    form = LevelForm()
    session = SessionLocal()
    try:
        result = session.execute(
            text("SELECT * FROM Levels.vw_ListLevels WHERE idLevel = :id"),
            {'id': id}
        ).fetchone()
        if not result:
            flash("Nivel no encontrado.", 'warning')
            return redirect(url_for('Levels.index'))

        if request.method == 'GET':
            for field in form:
                if field.name in result.keys():
                    field.data = result[field.name]

        if form.validate_on_submit():
            params = {
                key: value for key, value in form.data.items()
                if key != 'submit'
            }
            params['id'] = id
            params['updatedAt'] = datetime.datetime.utcnow()

            sql = ("EXEC Levels.sp_UpdateLevel "
                   "@id = :id, @name = :name, @description = :description, "
                   "@order = :order, @updatedAt = :updatedAt")
            session.execute(text(sql), params)
            session.commit()
            flash("Nivel actualizado exitosamente.", 'success')
            return redirect(url_for('Levels.index'))
    except Exception as e:
        session.rollback()
        flash(f"Error al editar nivel: {str(e)}", 'danger')
    finally:
        session.close()

    return render_template('Levels/level_form.html', form=form, title="Editar Nivel")

@bp.route('/delete/<int:id>', methods=['POST'])
def delete_level(id):
    session = SessionLocal()
    try:
        sql = text("EXEC Levels.sp_DeleteLevel @idLevelToDelete = :id")
        session.execute(sql, {'id': id})
        session.commit()
        flash("Nivel eliminado correctamente.", 'success')
    except Exception as e:
        session.rollback()
        flash(f"Error al eliminar nivel: {str(e)}", 'danger')
    finally:
        session.close()

    return redirect(url_for('Levels.index'))

@bp.route('/<int:id>')
def detail_level(id):
    session = SessionLocal()
    try:
        query = text("SELECT * FROM Levels.vw_ListLevels WHERE idLevel = :id")
        result = session.execute(query, {"id": id}).fetchone()
        if not result:
            flash("Nivel no encontrado.", 'warning')
            return redirect(url_for('Levels.index'))
    finally:
        session.close()

    return render_template('Levels/detail_level.html', detail=result, title="Detalle del Nivel")
