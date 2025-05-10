from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, IntegerField, TextAreaField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Optional, Length, Email, Regexp, NumberRange

class DataSheetForm(FlaskForm):
    # --- Catequizado ---
    c_firstName = StringField('Primer Nombre (Catequizado)', validators=[DataRequired(), Length(max=30)])
    c_secondName = StringField('Segundo Nombre (Catequizado)', validators=[Optional(), Length(max=30)])
    c_lastName = StringField('Primer Apellido (Catequizado)', validators=[DataRequired(), Length(max=30)])
    c_secondLastName = StringField('Segundo Apellido (Catequizado)', validators=[Optional(), Length(max=30)])
    c_sex = SelectField('Sexo (Catequizado)', choices=[('', '-- Seleccione --'), ('M', 'Masculino'), ('F', 'Femenino')], validators=[DataRequired()])
    ds_sonNumbr = IntegerField('Hijo Número (Ej: 1 para primogénito)', validators=[Optional(), NumberRange(min=0)])
    ds_numbrBrothers = IntegerField('Número de Hermanos', validators=[Optional(), NumberRange(min=0)])
    ds_livesWith = StringField('Vive Con', validators=[Optional(), Length(max=50)])
    ds_residentialPhone = StringField('Teléfono Residencial', validators=[Optional(), Length(max=15), Regexp(r'^\+?1?\d{7,15}$', message="Número de teléfono inválido.")])
    ds_mainAddress = TextAreaField('Dirección Principal', validators=[Optional(), Length(max=150)])

    c_birthdate = DateField('Fecha de Nacimiento (Catequizado)', format='%Y-%m-%d', validators=[DataRequired()])
    c_bloodType = StringField('Tipo de Sangre (Catequizado)', validators=[DataRequired(), Length(max=5)])
    c_alergies = TextAreaField('Alergias (Catequizado)', validators=[Optional()])
    c_emergencyContactName = StringField('Nombre Contacto de Emergencia', validators=[DataRequired(), Length(max=50)])
    c_emergencyContactPhone = StringField('Teléfono Contacto de Emergencia', validators=[DataRequired(), Length(max=15), Regexp(r'^\+?1?\d{7,15}$', message="Número de teléfono inválido.")])
    c_details = TextAreaField('Detalles Adicionales (Catequizado)', validators=[Optional()])
    c_idInstitution = IntegerField('ID Parroquia del Catequizado (Opcional)', validators=[Optional()]) # Debería ser un SelectField si cargas las parroquias
    # c_state = BooleanField('Estado Activo', default=True) # El SP ya tiene default, no es necesario en el form a menos que quieras cambiarlo

    # --- Padre ---
    f_firstName = StringField('Primer Nombre (Padre)', validators=[Optional(), Length(max=30)])
    f_secondName = StringField('Segundo Nombre (Padre)', validators=[Optional(), Length(max=30)])
    f_lastName = StringField('Primer Apellido (Padre)', validators=[Optional(), Length(max=30)])
    f_secondLastName = StringField('Segundo Apellido (Padre)', validators=[Optional(), Length(max=30)])
    f_ocupation = StringField('Ocupación (Padre)', validators=[Optional(), Length(max=50)])
    f_phoneContact = StringField('Teléfono (Padre)', validators=[Optional(), Length(max=15), Regexp(r'^\+?1?\d{7,15}$', message="Número de teléfono inválido.")])
    f_emailContact = StringField('Email (Padre)', validators=[Optional(), Email(), Length(max=50)])

    # --- Madre ---
    m_firstName = StringField('Primer Nombre (Madre)', validators=[Optional(), Length(max=30)])
    m_secondName = StringField('Segundo Nombre (Madre)', validators=[Optional(), Length(max=30)])
    m_lastName = StringField('Primer Apellido (Madre)', validators=[Optional(), Length(max=30)])
    m_secondLastName = StringField('Segundo Apellido (Madre)', validators=[Optional(), Length(max=30)])
    m_ocupation = StringField('Ocupación (Madre)', validators=[Optional(), Length(max=50)])
    m_phoneContact = StringField('Teléfono (Madre)', validators=[Optional(), Length(max=15), Regexp(r'^\+?1?\d{7,15}$', message="Número de teléfono inválido.")])
    m_emailContact = StringField('Email (Madre)', validators=[Optional(), Email(), Length(max=50)])

    # --- Iglesia y Nivel (Ficha) ---
    ds_idInstitution = IntegerField('ID Institución (Ficha - Opcional)', validators=[Optional()]) # Debería ser SelectField
    ds_idCertificate = IntegerField('ID Certificado Asociado (Opcional)', validators=[Optional()])
    ds_idLevel = IntegerField('ID Nivel de Inscripción (Opcional)', validators=[Optional()]) # Debería ser SelectField

    # --- Información Escolar (Ficha) ---
    ds_schoolsName = StringField('Nombre de la Escuela', validators=[DataRequired(), Length(max=100)])
    ds_schoolGrade = StringField('Grado/Curso Escolar', validators=[DataRequired(), Length(max=30)])

    submit = SubmitField('Guardar Hoja de Datos')