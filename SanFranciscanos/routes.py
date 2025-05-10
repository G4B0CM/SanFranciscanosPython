from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from sqlalchemy import text
from .forms import DataSheetForm
import datetime # Necesario para conversión de fechas si el formulario no lo hace automáticamente

bp = Blueprint('Documents', __name__, url_prefix='/Documents')

@bp.route('/new', methods=['GET', 'POST'])
def new_data_sheet():
    form = DataSheetForm()
    if form.validate_on_submit():

        params = {
            "c_firstName": form.c_firstName.data,
            "c_secondName": form.c_secondName.data or None,
            "c_lastName": form.c_lastName.data,
            "c_secondLastName": form.c_secondLastName.data or None,
            "c_sex": form.c_sex.data,
            "ds_sonNumbr": form.ds_sonNumbr.data,
            "ds_numbrBrothers": form.ds_numbrBrothers.data,
            "ds_livesWith": form.ds_livesWith.data or None,
            "ds_residentialPhone": form.ds_residentialPhone.data or None,
            "ds_mainAddress": form.ds_mainAddress.data or None,
            "c_birthdate": form.c_birthdate.data,
            "c_bloodType": form.c_bloodType.data,
            "c_alergies": form.c_alergies.data or None,
            "c_emergencyContactName": form.c_emergencyContactName.data,
            "c_emergencyContactPhone": form.c_emergencyContactPhone.data,
            "c_details": form.c_details.data or None,
            "c_idInstitution": form.c_idInstitution.data,
            "c_state": True, 

            "f_firstName": form.f_firstName.data or None,
            "f_secondName": form.f_secondName.data or None,
            "f_lastName": form.f_lastName.data or None,
            "f_secondLastName": form.f_secondLastName.data or None,
            "f_ocupation": form.f_ocupation.data or None,
            "f_phoneContact": form.f_phoneContact.data or None,
            "f_emailContact": form.f_emailContact.data or None,

            "m_firstName": form.m_firstName.data or None,
            "m_secondName": form.m_secondName.data or None,
            "m_lastName": form.m_lastName.data or None,
            "m_secondLastName": form.m_secondLastName.data or None,
            "m_ocupation": form.m_ocupation.data or None,
            "m_phoneContact": form.m_phoneContact.data or None,
            "m_emailContact": form.m_emailContact.data or None,

            "ds_idInstitution": form.ds_idInstitution.data,
            "ds_idCertificate": form.ds_idCertificate.data,
            "ds_idLevel": form.ds_idLevel.data,
            "ds_schoolsName": form.ds_schoolsName.data,
            "ds_schoolGrade": form.ds_schoolGrade.data,
        }

        SessionLocal = current_app.SessionLocal
        session = SessionLocal()

        try:
            # Construir la llamada al Stored Procedure
            # Asegúrate que los nombres de los parámetros en el SQL coincidan con los del SP
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
            """) # El nombre del SP en mi ejemplo anterior era sp_InsertDataSheet_WithPersonCreation, ajusta si es necesario
            
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
            print(f"Error en SP: {e}")
        finally:
            session.close()

    return render_template('Documents/data_sheet_form.html', form=form, title="Ingresar Hoja de Datos")

