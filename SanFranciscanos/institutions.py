from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from sqlalchemy import text
from .forms import ArquidiocesisForm, VicariaForm, ParroquiaForm, DeleteForm
import datetime
from SanFranciscanos.db import SessionLocal  # Importar la sesión de la base de datos

bp = Blueprint('Institutions', __name__, url_prefix='/Institutions')

def get_form_and_sp(institution_type):
    if institution_type == 'Arquidiocesis':
        return ArquidiocesisForm(), 'sp_InsertArquidiocesis', 'arquidiocesis_form.html'
    elif institution_type == 'Vicaria':
        return VicariaForm(), 'sp_InsertVicaria', 'vicaria_form.html'
    elif institution_type == 'Parroquia':
        return ParroquiaForm(), 'sp_InsertParroquia', 'parroquia_form.html'
    return None, None, None

@bp.route('/', methods=['GET', 'POST'])
def index():
    return render_template('Institutions/select_type.html', title="Seleccionar Tipo de Institución")

@bp.route('/list/<institution_type>')
def list_institution(institution_type):
    session = SessionLocal()
    try:
        query = text(f"SELECT * FROM Institutions.vw_List{institution_type}s")
        results = session.execute(query).fetchall()
    except Exception as e:
        flash(f"Error al listar {institution_type}s: {str(e)}", 'danger')
        results = []
    finally:
        session.close()

    delete_form = DeleteForm()
    return render_template(f'Institutions/list_{institution_type.lower()}.html', institutions=results, institution_type=institution_type, delete_form=delete_form, title=f"Lista de {institution_type}s")

@bp.route('/new/<institution_type>', methods=['GET', 'POST'])
def new_institution(institution_type):
    form, sp_name, template_name = get_form_and_sp(institution_type)
    if not form:
        flash('Tipo de institución no reconocido.', 'danger')
        return redirect(url_for('Institutions.index'))

    if form.validate_on_submit():
        params = {key: value for key, value in form.data.items() if key != 'submit' and value != ''}
        params['createdAt'] = datetime.datetime.utcnow()
        params['updatedAt'] = datetime.datetime.utcnow()
        params['state'] = 'Activo'
        session = SessionLocal()
        try:
            sql = f"EXEC Institutions.{sp_name} " + ", ".join([f"@{k} = :{k}" for k in params.keys()])
            session.execute(text(sql), params)
            session.commit()
            flash(f"{institution_type} creada exitosamente.", 'success')
            return redirect(url_for('Institutions.list_institution', institution_type=institution_type))
        except Exception as e:
            session.rollback()
            flash(f"Error al crear {institution_type}: {str(e)}", 'danger')
        finally:
            session.close()

    return render_template(f'Institutions/{template_name}', form=form, title=f'Nueva {institution_type}')

@bp.route('/edit/<institution_type>/<int:id>', methods=['GET', 'POST'])
def edit_institution(institution_type, id):
    form, _, template_name = get_form_and_sp(institution_type)
    if not form:
        flash('Tipo de institución no reconocido.', 'danger')
        return redirect(url_for('Institutions.index'))

    session = SessionLocal()
    try:
        query = text(f"SELECT * FROM Institutions.vw_List{institution_type}s WHERE id{institution_type} = :id")
        result = session.execute(query, {"id": id}).fetchone()
        if not result:
            flash(f"{institution_type} no encontrada.", 'warning')
            return redirect(url_for('Institutions.list_institution', institution_type=institution_type))

        if request.method == 'GET':
            for field in form:
                if field.name in result.keys():
                    field.data = result[field.name]

        if form.validate_on_submit():
            params = {key: value for key, value in form.data.items() if key != 'submit'}
            params['id'] = id
            params['updatedAt'] = datetime.datetime.utcnow()
            update_sp = f"sp_Update{institution_type}"
            sql = f"EXEC Institutions.{update_sp} " + ", ".join([f"@{k} = :{k}" for k in params.keys()])
            session.execute(text(sql), params)
            session.commit()
            flash(f"{institution_type} actualizada exitosamente.", 'success')
            return redirect(url_for('Institutions.list_institution', institution_type=institution_type))

    except Exception as e:
        session.rollback()
        flash(f"Error al editar {institution_type}: {str(e)}", 'danger')
    finally:
        session.close()

    return render_template(f'Institutions/{template_name}', form=form, title=f'Editar {institution_type}')

@bp.route('/delete/<institution_type>/<int:id>', methods=['POST'])
def delete_institution(institution_type, id):
    session = SessionLocal()
    try:
        sp_delete = f"sp_Delete{institution_type}"
        sql = text(f"EXEC Institutions.{sp_delete} @id{institution_type}ToDelete = :id")
        session.execute(sql, {"id": id})
        session.commit()
        flash(f"{institution_type} eliminada correctamente.", 'success')
    except Exception as e:
        session.rollback()
        flash(f"Error al eliminar {institution_type}: {str(e)}", 'danger')
    finally:
        session.close()

    return redirect(url_for('Institutions.list_institution', institution_type=institution_type))

@bp.route('/<institution_type>/<int:id>')
def detail_institution(institution_type, id):
    session = SessionLocal()
    try:
        query = text(f"SELECT * FROM Institutions.vw_List{institution_type}s WHERE id{institution_type} = :id")
        result = session.execute(query, {"id": id}).fetchone()
        if not result:
            flash(f"{institution_type} no encontrada.", 'warning')
            return redirect(url_for('Institutions.list_institution', institution_type=institution_type))
    finally:
        session.close()

    return render_template(f'Institutions/detail_{institution_type.lower()}.html', institution=result, title=f"Detalle de {institution_type}")
