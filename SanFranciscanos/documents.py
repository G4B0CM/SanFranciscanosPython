from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, abort
from sqlalchemy import text, select
from .forms import DataSheetForm,DeleteForm
from .models import Institution, Parroquia, Level, DataSheet, Catequizado, Person, Parent # Importar los modelos necesarios
import datetime


bp = Blueprint('Documents', __name__, url_prefix='/Documents') 

# --- FUNCIÓN AUXILIAR PARA CARGAR OPCIONES DE SELECTS (REUTILIZABLE) ---
def load_select_field_options(form):
    SessionLocal = current_app.SessionLocal
    db_session = SessionLocal()
    try:
        # Cargar Parroquias
        parroquias_query = db_session.execute(
            select(Institution).where(Institution.type == 'Parroquia').order_by(Institution.name)
        )
        parroquias = parroquias_query.scalars().all()
        parroquia_choices = [('', '-- Seleccione Parroquia --')] + [(p.idInstitution, p.name) for p in parroquias]
        form.c_idInstitution.choices = parroquia_choices
        form.ds_idInstitution.choices = parroquia_choices

        # Cargar Niveles
        niveles_query = db_session.execute(select(Level).order_by(Level.numberOfOrder, Level.name))
        niveles = niveles_query.scalars().all()
        form.ds_idLevel.choices = [('', '-- Seleccione Nivel --')] + [(n.idLevel, n.name) for n in niveles]
    except Exception as e:
        flash(f'Error cargando opciones del formulario: {str(e)}', 'danger')
        print(f"Error cargando opciones: {e}")
    finally:
        db_session.close()



@bp.route('/new', methods=['GET', 'POST'])
def new_data_sheet():
    form = DataSheetForm()
    load_select_field_options(form) 

    if form.validate_on_submit():
        params = {
            "c_firstName": form.c_firstName.data, "c_secondName": form.c_secondName.data or None,
            "c_lastName": form.c_lastName.data, "c_secondLastName": form.c_secondLastName.data or None,
            "c_sex": form.c_sex.data, "ds_sonNumbr": form.ds_sonNumbr.data if form.ds_sonNumbr.data is not None else None,
            "ds_numbrBrothers": form.ds_numbrBrothers.data if form.ds_numbrBrothers.data is not None else None,
            "ds_livesWith": form.ds_livesWith.data or None, "ds_residentialPhone": form.ds_residentialPhone.data or None,
            "ds_mainAddress": form.ds_mainAddress.data or None, "c_birthdate": form.c_birthdate.data,
            "c_bloodType": form.c_bloodType.data, "c_alergies": form.c_alergies.data or None,
            "c_emergencyContactName": form.c_emergencyContactName.data,
            "c_emergencyContactPhone": form.c_emergencyContactPhone.data, "c_details": form.c_details.data or None,
            "c_idInstitution": form.c_idInstitution.data if form.c_idInstitution.data else None, "c_state": True,
            "f_firstName": form.f_firstName.data or None, "f_secondName": form.f_secondName.data or None,
            "f_lastName": form.f_lastName.data or None, "f_secondLastName": form.f_secondLastName.data or None,
            "f_ocupation": form.f_ocupation.data or None, "f_phoneContact": form.f_phoneContact.data or None,
            "f_emailContact": form.f_emailContact.data or None, "m_firstName": form.m_firstName.data or None,
            "m_secondName": form.m_secondName.data or None, "m_lastName": form.m_lastName.data or None,
            "m_secondLastName": form.m_secondLastName.data or None, "m_ocupation": form.m_ocupation.data or None,
            "m_phoneContact": form.m_phoneContact.data or None, "m_emailContact": form.m_emailContact.data or None,
            "ds_idInstitution": form.ds_idInstitution.data if form.ds_idInstitution.data else None,
            "ds_idCertificate": form.ds_idCertificate.data if form.ds_idCertificate.data is not None else None,
            "ds_idLevel": form.ds_idLevel.data if form.ds_idLevel.data else None,
            "ds_schoolsName": form.ds_schoolsName.data, "ds_schoolGrade": form.ds_schoolGrade.data,
        }
        SessionLocal = current_app.SessionLocal
        session = SessionLocal()
        try:
            sql_query = text("""
                DECLARE @CreatedDataSheetID INT;
                EXEC Documents.sp_InsertDataSheet
                    @c_firstName = :c_firstName, @c_secondName = :c_secondName, @c_lastName = :c_lastName,
                    @c_secondLastName = :c_secondLastName, @c_sex = :c_sex, @ds_sonNumbr = :ds_sonNumbr,
                    @ds_numbrBrothers = :ds_numbrBrothers, @ds_livesWith = :ds_livesWith,
                    @ds_residentialPhone = :ds_residentialPhone, @ds_mainAddress = :ds_mainAddress,
                    @c_birthdate = :c_birthdate, @c_bloodType = :c_bloodType, @c_alergies = :c_alergies,
                    @c_emergencyContactName = :c_emergencyContactName, @c_emergencyContactPhone = :c_emergencyContactPhone,
                    @c_details = :c_details, @c_idInstitution = :c_idInstitution, @c_state = :c_state,
                    @f_firstName = :f_firstName, @f_secondName = :f_secondName, @f_lastName = :f_lastName,
                    @f_secondLastName = :f_secondLastName, @f_ocupation = :f_ocupation,
                    @f_phoneContact = :f_phoneContact, @f_emailContact = :f_emailContact,
                    @m_firstName = :m_firstName, @m_secondName = :m_secondName, @m_lastName = :m_lastName,
                    @m_secondLastName = :m_secondLastName, @m_ocupation = :m_ocupation,
                    @m_phoneContact = :m_phoneContact, @m_emailContact = :m_emailContact,
                    @ds_idInstitution = :ds_idInstitution, @ds_idCertificate = :ds_idCertificate,
                    @ds_idLevel = :ds_idLevel, @ds_schoolsName = :ds_schoolsName,
                    @ds_schoolGrade = :ds_schoolGrade,
                    @CreatedDataSheetID = @CreatedDataSheetID OUTPUT;
                SELECT @CreatedDataSheetID AS CreatedDataSheetID;
            """)
            result = session.execute(sql_query, params)
            created_id = result.scalar_one_or_none()
            session.commit()
            if created_id:
                flash(f'Hoja de Datos creada exitosamente con ID: {created_id}.', 'success')
                return redirect(url_for('Documents.new_data_sheet'))
            else:
                flash('Error al crear la Hoja de Datos: no se obtuvo ID.', 'danger')
        except Exception as e:
            session.rollback()
            flash(f'Error al guardar la Hoja de Datos: {str(e)}', 'danger')
            print(f"Error en SP INSERT: {e}")
        finally:
            session.close()
    return render_template('Documents/data_sheet_form.html', form=form, title="Ingresar Hoja de Datos", action_url=url_for('Documents.new_data_sheet'))



@bp.route('/update/<int:datasheet_id>', methods=['GET', 'POST'])
def update_data_sheet(datasheet_id):
    SessionLocal = current_app.SessionLocal
    session = SessionLocal()
    
    
    data_sheet_obj = session.get(DataSheet, datasheet_id) 

    if not data_sheet_obj:
        session.close()
        abort(404) # Hoja de Datos no encontrada

    # Recuperar Catequizado y su Person base
    catequizado_obj = None
    person_catequizado_obj = None
    if data_sheet_obj.idCatequizado:
        catequizado_obj = session.get(Catequizado, data_sheet_obj.idCatequizado)
        if catequizado_obj: 
             person_catequizado_obj = catequizado_obj 

    
    papa_obj = None
    person_papa_obj = None
    if data_sheet_obj.idPapa:
        papa_obj = session.get(Parent, data_sheet_obj.idPapa) 
        if papa_obj:
            person_papa_obj = session.get(Person, papa_obj.idPerson)


    
    mama_obj = None
    person_mama_obj = None
    if data_sheet_obj.idMama:
        mama_obj = session.get(Parent, data_sheet_obj.idMama)
        if mama_obj:
            person_mama_obj = session.get(Person, mama_obj.idPerson)

    
    form = DataSheetForm(obj=data_sheet_obj) 
    
    load_select_field_options(form) 

    if request.method == 'GET':
  
        form.ds_sonNumbr.data = data_sheet_obj.sonNumbr
        form.ds_numbrBrothers.data = data_sheet_obj.numbrBrothers
        form.ds_livesWith.data = data_sheet_obj.livesWith
        form.ds_residentialPhone.data = data_sheet_obj.residentialPhone
        form.ds_mainAddress.data = data_sheet_obj.mainAddress
        form.ds_idInstitution.data = data_sheet_obj.idInstitution 
        form.ds_idCertificate.data = data_sheet_obj.idCertificate
        form.ds_idLevel.data = data_sheet_obj.idLevel 
        form.ds_schoolsName.data = data_sheet_obj.schoolsName
        form.ds_schoolGrade.data = data_sheet_obj.schoolGrade

        if person_catequizado_obj and catequizado_obj:
            form.c_firstName.data = person_catequizado_obj.firstName
            form.c_secondName.data = person_catequizado_obj.secondName
            form.c_lastName.data = person_catequizado_obj.lastName
            form.c_secondLastName.data = person_catequizado_obj.secondLastName
            form.c_sex.data = person_catequizado_obj.sex
            form.c_birthdate.data = catequizado_obj.birthdate
            form.c_bloodType.data = catequizado_obj.bloodType
            form.c_alergies.data = catequizado_obj.alergies
            form.c_emergencyContactName.data = catequizado_obj.emergencyContactName
            form.c_emergencyContactPhone.data = catequizado_obj.emergencyContactPhone
            form.c_details.data = catequizado_obj.details
            form.c_idInstitution.data = catequizado_obj.idInstitution # Para el SelectField

       
        if person_papa_obj and papa_obj:
            form.f_firstName.data = person_papa_obj.firstName
            form.f_secondName.data = person_papa_obj.secondName
            form.f_lastName.data = person_papa_obj.lastName
            form.f_secondLastName.data = person_papa_obj.secondLastName
            form.f_ocupation.data = papa_obj.ocupation
            form.f_phoneContact.data = papa_obj.phoneContact
            form.f_emailContact.data = papa_obj.emailContact
        
        
        if person_mama_obj and mama_obj:
            form.m_firstName.data = person_mama_obj.firstName
            form.m_secondName.data = person_mama_obj.secondName
            form.m_lastName.data = person_mama_obj.lastName
            form.m_secondLastName.data = person_mama_obj.secondLastName
            form.m_ocupation.data = mama_obj.ocupation
            form.m_phoneContact.data = mama_obj.phoneContact
            form.m_emailContact.data = mama_obj.emailContact

    if form.validate_on_submit(): 
        params_update = {
            "idDataSheetToUpdate": datasheet_id,
            "c_firstName": form.c_firstName.data, "c_secondName": form.c_secondName.data or None,
            "c_lastName": form.c_lastName.data, "c_secondLastName": form.c_secondLastName.data or None,
            "c_sex": form.c_sex.data, "ds_sonNumbr": form.ds_sonNumbr.data if form.ds_sonNumbr.data is not None else None,
            "ds_numbrBrothers": form.ds_numbrBrothers.data if form.ds_numbrBrothers.data is not None else None,
            "ds_livesWith": form.ds_livesWith.data or None, "ds_residentialPhone": form.ds_residentialPhone.data or None,
            "ds_mainAddress": form.ds_mainAddress.data or None, "c_birthdate": form.c_birthdate.data,
            "c_bloodType": form.c_bloodType.data, "c_alergies": form.c_alergies.data or None,
            "c_emergencyContactName": form.c_emergencyContactName.data,
            "c_emergencyContactPhone": form.c_emergencyContactPhone.data, "c_details": form.c_details.data or None,
            "c_idInstitution_Catequizado": form.c_idInstitution.data if form.c_idInstitution.data else None, 
            "c_state": catequizado_obj.state if catequizado_obj else True, 

            "f_firstName": form.f_firstName.data or None, "f_secondName": form.f_secondName.data or None,
            "f_lastName": form.f_lastName.data or None, "f_secondLastName": form.f_secondLastName.data or None,
            "f_ocupation": form.f_ocupation.data or None, "f_phoneContact": form.f_phoneContact.data or None,
            "f_emailContact": form.f_emailContact.data or None, 
            
            "m_firstName": form.m_firstName.data or None, "m_secondName": form.m_secondName.data or None,
            "m_lastName": form.m_lastName.data or None, "m_secondLastName": form.m_secondLastName.data or None,
            "m_ocupation": form.m_ocupation.data or None, "m_phoneContact": form.m_phoneContact.data or None,
            "m_emailContact": form.m_emailContact.data or None,

            "ds_idInstitution_Ficha": form.ds_idInstitution.data if form.ds_idInstitution.data else None, 
            "ds_idCertificate": form.ds_idCertificate.data if form.ds_idCertificate.data is not None else None,
            "ds_idLevel": form.ds_idLevel.data if form.ds_idLevel.data else None,
            "ds_schoolsName": form.ds_schoolsName.data, "ds_schoolGrade": form.ds_schoolGrade.data,
        }
        
        try:
            sql_query_update = text("""
                EXEC Documents.sp_UpdateDataSheet
                    @idDataSheetToUpdate = :idDataSheetToUpdate,
                    @c_firstName = :c_firstName, @c_secondName = :c_secondName, @c_lastName = :c_lastName,
                    @c_secondLastName = :c_secondLastName, @c_sex = :c_sex, @ds_sonNumbr = :ds_sonNumbr,
                    @ds_numbrBrothers = :ds_numbrBrothers, @ds_livesWith = :ds_livesWith,
                    @ds_residentialPhone = :ds_residentialPhone, @ds_mainAddress = :ds_mainAddress,
                    @c_birthdate = :c_birthdate, @c_bloodType = :c_bloodType, @c_alergies = :c_alergies,
                    @c_emergencyContactName = :c_emergencyContactName, @c_emergencyContactPhone = :c_emergencyContactPhone,
                    @c_details = :c_details, @c_idInstitution_Catequizado = :c_idInstitution_Catequizado, @c_state = :c_state,
                    @f_firstName = :f_firstName, @f_secondName = :f_secondName, @f_lastName = :f_lastName,
                    @f_secondLastName = :f_secondLastName, @f_ocupation = :f_ocupation,
                    @f_phoneContact = :f_phoneContact, @f_emailContact = :f_emailContact,
                    @m_firstName = :m_firstName, @m_secondName = :m_secondName, @m_lastName = :m_lastName,
                    @m_secondLastName = :m_secondLastName, @m_ocupation = :m_ocupation,
                    @m_phoneContact = :m_phoneContact, @m_emailContact = :m_emailContact,
                    @ds_idInstitution_Ficha = :ds_idInstitution_Ficha, @ds_idCertificate = :ds_idCertificate,
                    @ds_idLevel = :ds_idLevel, @ds_schoolsName = :ds_schoolsName,
                    @ds_schoolGrade = :ds_schoolGrade;
            """) 
            
            session.execute(sql_query_update, params_update)
            session.commit()
            flash('Hoja de Datos actualizada exitosamente.', 'success')
            return redirect(url_for('Documents.update_data_sheet', datasheet_id=datasheet_id)) 
        except Exception as e:
            session.rollback()
            flash(f'Error al actualizar la Hoja de Datos: {str(e)}', 'danger')
            print(f"Error en SP UPDATE: {e}")

    session.close()
    return render_template('Documents/data_sheet_form.html', form=form, title=f"Actualizar Hoja de Datos ID: {datasheet_id}", action_url=url_for('Documents.update_data_sheet', datasheet_id=datasheet_id))


@bp.route('/')
def index():
    return redirect(url_for('Documents.new_data_sheet'))

@bp.route('/list')
def list_data_sheets():
    SessionLocal = current_app.SessionLocal
    session = SessionLocal()
    try:
        query = text("""
            SELECT ds.idDataSheet, p.firstName, p.lastName, ds.schoolsName
            FROM Documents.DataSheet ds
            LEFT JOIN Persons.Catequizado c ON ds.idCatequizado = c.idPerson
            LEFT JOIN Persons.Person p ON c.idPerson = p.idPerson
            ORDER BY ds.idDataSheet DESC;
        """)
        result = session.execute(query)
        datasheets_list = result.fetchall() 
    except Exception as e:
        flash(f"Error al cargar la lista de hojas de datos: {str(e)}", "danger")
        datasheets_list = []
    finally:
        session.close()
    
    delete_form = DeleteForm()
    return render_template('Documents/list_data_sheets.html',
                           datasheets=datasheets_list,
                           title="Lista de Hojas de Datos",
                           delete_form=delete_form)



@bp.route('/delete/<int:datasheet_id>', methods=['POST'])
def delete_data_sheet(datasheet_id):
    SessionLocal = current_app.SessionLocal
    session = SessionLocal()
    try:

        sql_query_delete = text("""
            EXEC Documents.sp_DeleteDataSheet @idDataSheetToDelete = :idDataSheet;
        """)
        
        session.execute(sql_query_delete, {"idDataSheet": datasheet_id})
        session.commit()
        flash(f'Hoja de Datos ID {datasheet_id} y entidades relacionadas eliminadas exitosamente.', 'success')

    except Exception as e:
        session.rollback()
        flash(f'Error al eliminar la Hoja de Datos: {str(e)}', 'danger')
        print(f"Error en SP DELETE: {e}")
    finally:
        session.close()
    
    return redirect(url_for('Documents.list_data_sheets'))