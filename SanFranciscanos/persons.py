from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, abort
from sqlalchemy import text
from .forms import CatequistaForm, AyudanteForm, EclesiasticoForm, PadrinoForm, PadreMadreForm, RolSelectorForm, DeleteForm
import datetime

bp = Blueprint('Persons', __name__, url_prefix='/Persons')

# Vista inicial para seleccionar el rol
def get_form_for_role(role):
    if role == 'Catequista':
        return CatequistaForm(), 'sp_InsertCatequista', 'catequista_form.html'
    elif role == 'Ayudante':
        return AyudanteForm(), 'sp_InsertAyudante', 'ayudante_form.html'
    elif role == 'Eclesiastico':
        return EclesiasticoForm(), 'sp_InsertEclesiastico', 'eclesiastico_form.html'
    elif role == 'Padrino':
        return PadrinoForm(), 'sp_InsertPadrino', 'padrino_form.html'
    elif role == 'PadreMadre':
        return PadreMadreForm(), 'sp_InsertParent', 'padremadre_form.html'
    else:
        return None, None, None

@bp.route('/', methods=['GET', 'POST'])
def index():
    form = RolSelectorForm()
    if form.validate_on_submit():
        role = form.role.data
        return redirect(url_for('Persons.new_person', role=role))
    return render_template('Persons/select_role.html', form=form, title="Seleccionar Rol")

@bp.route('/new/<role>', methods=['GET', 'POST'])
def new_person(role):
    form, sp_name, template_name = get_form_for_role(role)
    if not form:
        flash('Rol no reconocido.', 'danger')
        return redirect(url_for('Persons.index'))

    if form.validate_on_submit():
        params = {key: value for key, value in form.data.items() if key != 'submit' and value != ''}
        params['createdAt'] = datetime.datetime.utcnow()
        params['updatedAt'] = datetime.datetime.utcnow()
        params['state'] = 'Activo'
        SessionLocal = current_app.SessionLocal
        session = SessionLocal()
        try:
            sql = f"EXEC Persons.{sp_name} " + ", ".join([f"@{k} = :{k}" for k in params.keys()])
            session.execute(text(sql), params)
            session.commit()
            flash(f'{role} creado exitosamente.', 'success')
            return redirect(url_for('Persons.index'))
        except Exception as e:
            session.rollback()
            flash(f"Error al crear {role}: {str(e)}", 'danger')
        finally:
            session.close()

    return render_template(f'Persons/{template_name}', form=form, title=f'Nuevo {role}')

@bp.route('/list/<role>')
def list_persons(role):
    SessionLocal = current_app.SessionLocal
    session = SessionLocal()
    try:
        query = text(f"SELECT * FROM Persons.vw_List{role}")
        results = session.execute(query).fetchall()
    except Exception as e:
        flash(f"Error al listar {role}: {str(e)}", 'danger')
        results = []
    finally:
        session.close()

    delete_form = DeleteForm()
    return render_template(f'Persons/list_{role.lower()}.html', persons=results, role=role, delete_form=delete_form, title=f"Lista de {role}s")

@bp.route('/delete/<role>/<int:id>', methods=['POST'])
def delete_person(role, id):
    SessionLocal = current_app.SessionLocal
    session = SessionLocal()
    try:
        sp_delete = f"sp_Delete{role}"
        sql = text(f"EXEC Persons.{sp_delete} @idPersonToDelete = :id")
        session.execute(sql, {"id": id})
        session.commit()
        flash(f'{role} eliminado correctamente.', 'success')
    except Exception as e:
        session.rollback()
        flash(f"Error al eliminar {role}: {str(e)}", 'danger')
    finally:
        session.close()

    return redirect(url_for('Persons.list_persons', role=role))

@bp.route('/edit/<role>/<int:id>', methods=['GET', 'POST'])
def edit_person(role, id):
    form, _, template_name = get_form_for_role(role)
    if not form:
        flash('Rol no reconocido.', 'danger')
        return redirect(url_for('Persons.index'))

    SessionLocal = current_app.SessionLocal
    session = SessionLocal()
    try:
        query = text(f"SELECT * FROM Persons.vw_List{role} WHERE idPerson = :id")
        result = session.execute(query, {"id": id}).fetchone()
        if not result:
            flash(f"{role} no encontrado.", 'warning')
            return redirect(url_for('Persons.list_persons', role=role))

        if request.method == 'GET':
            for field in form:
                if field.name in result.keys():
                    field.data = result[field.name]

        if form.validate_on_submit():
            update_sp = f"sp_Update{role}"
            params = {key: value for key, value in form.data.items() if key != 'submit'}
            params['id'] = id
            params['updatedAt'] = datetime.datetime.utcnow()
            sql = f"EXEC Persons.{update_sp} " + ", ".join([f"@{k} = :{k}" for k in params.keys()])
            session.execute(text(sql), params)
            session.commit()
            flash(f"{role} actualizado exitosamente.", 'success')
            return redirect(url_for('Persons.list_persons', role=role))

    except Exception as e:
        session.rollback()
        flash(f"Error al editar {role}: {str(e)}", 'danger')
    finally:
        session.close()

    return render_template(f'Persons/{template_name}', form=form, title=f'Editar {role}')

@bp.route('/<role>/<int:id>')
def detail_person(role, id):
    SessionLocal = current_app.SessionLocal
    session = SessionLocal()
    try:
        query = text(f"SELECT * FROM Persons.vw_List{role} WHERE idPerson = :id")
        result = session.execute(query, {"id": id}).fetchone()
        if not result:
            flash(f"{role} no encontrado.", 'warning')
            return redirect(url_for('Persons.list_persons', role=role))
    finally:
        session.close()

    return render_template(f'Persons/detail_{role.lower()}.html', detail=result, title=f"Detalle de {role}")
