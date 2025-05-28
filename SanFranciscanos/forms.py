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

class DeleteForm(FlaskForm):
    submit = SubmitField('Eliminar')
    
class CatequistaForm(FlaskForm):
    firstName = StringField('Primer Nombre', validators=[DataRequired(), Length(max=30)])
    secondName = StringField('Segundo Nombre', validators=[Optional(), Length(max=30)])
    lastName = StringField('Primer Apellido', validators=[DataRequired(), Length(max=30)])
    secondLastName = StringField('Segundo Apellido', validators=[Optional(), Length(max=30)])
    sex = SelectField('Sexo', choices=[('', '-- Seleccione --'), ('M', 'Masculino'), ('F', 'Femenino')], validators=[DataRequired()])
    birthdate = DateField('Fecha de Nacimiento', format='%Y-%m-%d', validators=[DataRequired()])
    bloodType = StringField('Tipo de Sangre', validators=[DataRequired(), Length(max=5)])
    emergencyContactName = StringField('Nombre Contacto de Emergencia', validators=[Optional(), Length(max=50)])
    emergencyContactPhone = StringField('Teléfono Emergencia', validators=[Optional(), Length(max=15), Regexp(r'^\+?1?\d{7,15}$')])
    idInstitution = IntegerField('ID Parroquia Asociada', validators=[Optional()])
    submit = SubmitField('Guardar Catequista')

class PadrinoForm(FlaskForm):
    firstName = StringField('Primer Nombre', validators=[DataRequired(), Length(max=30)])
    secondName = StringField('Segundo Nombre', validators=[Optional(), Length(max=30)])
    lastName = StringField('Primer Apellido', validators=[DataRequired(), Length(max=30)])
    secondLastName = StringField('Segundo Apellido', validators=[Optional(), Length(max=30)])
    sex = SelectField('Sexo', choices=[('', '-- Seleccione --'), ('M', 'Masculino'), ('F', 'Femenino')], validators=[DataRequired()])
    phoneContact = StringField('Teléfono', validators=[Optional(), Length(max=15), Regexp(r'^\+?1?\d{7,15}$')])
    emailContact = StringField('Correo Electrónico', validators=[Optional(), Email(), Length(max=50)])
    submit = SubmitField('Guardar Padrino')

class EclesiasticoForm(FlaskForm):
    firstName = StringField('Primer Nombre', validators=[DataRequired(), Length(max=30)])
    secondName = StringField('Segundo Nombre', validators=[Optional(), Length(max=30)])
    lastName = StringField('Primer Apellido', validators=[DataRequired(), Length(max=30)])
    secondLastName = StringField('Segundo Apellido', validators=[Optional(), Length(max=30)])
    phoneContact = StringField('Teléfono', validators=[Optional(), Length(max=15), Regexp(r'^\+?1?\d{7,15}$')])
    emailContact = StringField('Correo Electrónico', validators=[Optional(), Email(), Length(max=50)])
    submit = SubmitField('Guardar Eclesiástico')

class ParroquiaForm(FlaskForm):
    name = StringField('Nombre de la Parroquia', validators=[DataRequired(), Length(max=100)])
    address = StringField('Dirección', validators=[Optional(), Length(max=150)])
    phone = StringField('Teléfono de Contacto', validators=[Optional(), Length(max=15), Regexp(r'^\+?1?\d{7,15}$')])
    email = StringField('Correo Electrónico', validators=[Optional(), Email(), Length(max=50)])
    idVicaria = IntegerField('ID Vicaria a la que pertenece', validators=[DataRequired()])
    submit = SubmitField('Guardar Parroquia')

class VicariaForm(FlaskForm):
    name = StringField('Nombre de la Vicaria', validators=[DataRequired(), Length(max=100)])
    address = StringField('Dirección', validators=[Optional(), Length(max=150)])
    phone = StringField('Teléfono de Contacto', validators=[Optional(), Length(max=15), Regexp(r'^\+?1?\d{7,15}$')])
    email = StringField('Correo Electrónico', validators=[Optional(), Email(), Length(max=50)])
    idArquidiocesis = IntegerField('ID Arquidiócesis a la que pertenece', validators=[DataRequired()])
    submit = SubmitField('Guardar Vicaria')

class ArquidiocesisForm(FlaskForm):
    name = StringField('Nombre de la Arquidiócesis', validators=[DataRequired(), Length(max=100)])
    address = StringField('Dirección', validators=[Optional(), Length(max=150)])
    phone = StringField('Teléfono de Contacto', validators=[Optional(), Length(max=15), Regexp(r'^\+?1?\d{7,15}$')])
    email = StringField('Correo Electrónico', validators=[Optional(), Email(), Length(max=50)])
    submit = SubmitField('Guardar Arquidiócesis')

class LevelForm(FlaskForm):
    name = StringField('Nombre del Nivel', validators=[DataRequired(), Length(max=50)])
    description = TextAreaField('Descripción del Nivel', validators=[Optional(), Length(max=250)])
    order = IntegerField('Orden del Nivel', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Guardar Nivel')

class CursoForm(FlaskForm):
    name = StringField('Nombre del Curso', validators=[DataRequired(), Length(max=50)])
    idParroquia = IntegerField('ID Parroquia', validators=[DataRequired()])
    idCatequista = IntegerField('ID Catequista Responsable', validators=[DataRequired()])
    idLevel = IntegerField('ID Nivel Asociado', validators=[DataRequired()])
    startDate = DateField('Fecha de Inicio', format='%Y-%m-%d', validators=[DataRequired()])
    endDate = DateField('Fecha de Fin', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Guardar Curso')

class GruposForm(FlaskForm):
    idCatequizado = IntegerField('ID Catequizado', validators=[DataRequired()])
    idCurso = IntegerField('ID Curso', validators=[DataRequired()])
    fechaInscripcion = DateField('Fecha de Inscripción', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Guardar Inscripción en Grupo')

class SacramentForm(FlaskForm):
    name = StringField('Nombre del Sacramento', validators=[DataRequired(), Length(max=50)])
    description = TextAreaField('Descripción del Sacramento', validators=[Optional(), Length(max=250)])
    required = BooleanField('¿Es Requisito para Inscribirse a un Nivel?', default=False)
    submit = SubmitField('Guardar Sacramento')

class CatequizadoSacramentoForm(FlaskForm):
    idCatequizado = IntegerField('ID del Catequizado', validators=[DataRequired()])
    idSacramento = IntegerField('ID del Sacramento', validators=[DataRequired()])
    dateReceived = DateField('Fecha de Recepción', format='%Y-%m-%d', validators=[DataRequired()])
    lugar = StringField('Lugar del Sacramento', validators=[Optional(), Length(max=100)])
    observaciones = TextAreaField('Observaciones', validators=[Optional(), Length(max=250)])
    submit = SubmitField('Guardar Relación Catequizado-Sacramento')

