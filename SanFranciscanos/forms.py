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
    c_idInstitution = IntegerField('ID Parroquia del Catequizado (Opcional)', validators=[Optional()])
    ds_idInstitution = IntegerField('ID Institución (Ficha - Opcional)', validators=[Optional()])
    ds_idCertificate = IntegerField('ID Certificado Asociado (Opcional)', validators=[Optional()])
    ds_idLevel = IntegerField('ID Nivel de Inscripción (Opcional)', validators=[Optional()])
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

class AyudanteForm(FlaskForm):
    firstName = StringField('Primer Nombre', validators=[DataRequired(), Length(max=30)])
    secondName = StringField('Segundo Nombre', validators=[Optional(), Length(max=30)])
    lastName = StringField('Primer Apellido', validators=[DataRequired(), Length(max=30)])
    secondLastName = StringField('Segundo Apellido', validators=[Optional(), Length(max=30)])
    sex = SelectField('Sexo', choices=[('', '-- Seleccione --'), ('M', 'Masculino'), ('F', 'Femenino')], validators=[DataRequired()])
    birthdate = DateField('Fecha de Nacimiento', format='%Y-%m-%d', validators=[DataRequired()])
    bloodType = StringField('Tipo de Sangre', validators=[Optional(), Length(max=5)])
    emergencyContactName = StringField('Nombre Contacto de Emergencia', validators=[Optional(), Length(max=50)])
    emergencyContactPhone = StringField('Teléfono Emergencia', validators=[Optional(), Length(max=15), Regexp(r'^\+?1?\d{7,15}$')])
    idInstitution = IntegerField('ID Parroquia Asociada', validators=[Optional()])
    submit = SubmitField('Guardar Ayudante')

class EclesiasticoForm(FlaskForm):
    firstName = StringField('Primer Nombre', validators=[DataRequired(), Length(max=30)])
    secondName = StringField('Segundo Nombre', validators=[Optional(), Length(max=30)])
    lastName = StringField('Primer Apellido', validators=[DataRequired(), Length(max=30)])
    secondLastName = StringField('Segundo Apellido', validators=[Optional(), Length(max=30)])
    phoneContact = StringField('Teléfono', validators=[Optional(), Length(max=15), Regexp(r'^\+?1?\d{7,15}$')])
    emailContact = StringField('Correo Electrónico', validators=[Optional(), Email(), Length(max=50)])
    submit = SubmitField('Guardar Eclesiástico')

class PadrinoForm(FlaskForm):
    firstName = StringField('Primer Nombre', validators=[DataRequired(), Length(max=30)])
    secondName = StringField('Segundo Nombre', validators=[Optional(), Length(max=30)])
    lastName = StringField('Primer Apellido', validators=[DataRequired(), Length(max=30)])
    secondLastName = StringField('Segundo Apellido', validators=[Optional(), Length(max=30)])
    sex = SelectField('Sexo', choices=[('', '-- Seleccione --'), ('M', 'Masculino'), ('F', 'Femenino')], validators=[DataRequired()])
    phoneContact = StringField('Teléfono', validators=[Optional(), Length(max=15), Regexp(r'^\+?1?\d{7,15}$')])
    emailContact = StringField('Correo Electrónico', validators=[Optional(), Email(), Length(max=50)])
    submit = SubmitField('Guardar Padrino')

class PadreMadreForm(FlaskForm):
    firstName = StringField('Primer Nombre', validators=[DataRequired(), Length(max=30)])
    secondName = StringField('Segundo Nombre', validators=[Optional(), Length(max=30)])
    lastName = StringField('Primer Apellido', validators=[DataRequired(), Length(max=30)])
    secondLastName = StringField('Segundo Apellido', validators=[Optional(), Length(max=30)])
    ocupation = StringField('Ocupación', validators=[Optional(), Length(max=50)])
    phoneContact = StringField('Teléfono', validators=[Optional(), Length(max=15), Regexp(r'^\+?1?\d{7,15}$')])
    emailContact = StringField('Correo Electrónico', validators=[Optional(), Email(), Length(max=50)])
    idInstitution = IntegerField('ID Parroquia Asociada', validators=[Optional()])
    submit = SubmitField('Guardar Padre/Madre')

class InstitutionForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired(), Length(max=100)])
    type = StringField('Tipo', validators=[DataRequired(), Length(max=50)])
    location = StringField('Ubicación', validators=[DataRequired(), Length(max=100)])
    contact = StringField('Contacto', validators=[DataRequired(), Length(max=50)])
    submit = SubmitField('Guardar')

class LevelForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired(), Length(max=100)])
    description = StringField('Descripción', validators=[DataRequired(), Length(max=200)])
    order = IntegerField('Orden del Nivel', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Guardar')

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
    
class DocumentForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired(), Length(max=100)])
    type = StringField('Tipo', validators=[DataRequired(), Length(max=50)])
    description = TextAreaField('Descripción', validators=[Optional(), Length(max=250)])
    category = SelectField('Categoría', choices=[
        ('', '-- Seleccione una Categoría --'),
        ('Identidad', 'Identidad'),
        ('Educación', 'Educación'),
        ('Sacramentos', 'Sacramentos'),
        ('Salud', 'Salud'),
        ('Legal', 'Legal'),
        ('Otro', 'Otro')
    ], validators=[DataRequired()])
    submit = SubmitField('Guardar')

class CertificateForm(FlaskForm):
    idCatequizado = StringField('ID del Catequizado', validators=[DataRequired(message="Este campo es obligatorio.")])
    idSacramento = StringField('ID del Sacramento', validators=[DataRequired(message="Este campo es obligatorio.")])
    fechaEmision = DateField('Fecha de Emisión', format='%Y-%m-%d', validators=[DataRequired(message="Ingrese una fecha válida.")])
    lugar = StringField('Lugar de Emisión', validators=[DataRequired(), Length(min=3, max=100)])
    observaciones = TextAreaField('Observaciones', validators=[Length(max=300)])
    submit = SubmitField('Guardar')


class RolSelectorForm(FlaskForm):
    role = SelectField('Seleccionar Rol', choices=[
        ('', '-- Seleccione un Rol --'),
        ('Catequista', 'Catequista'),
        ('Ayudante', 'Ayudante'),
        ('Eclesiastico', 'Eclesiástico'),
        ('Padrino', 'Padrino'),
        ('PadreMadre', 'Padre/Madre')
    ], validators=[DataRequired()])
    submit = SubmitField('Continuar')

class AttendanceForm(FlaskForm):
    idCurso = IntegerField('ID del Curso', validators=[DataRequired()])
    idCatequizado = IntegerField('ID del Catequizado', validators=[DataRequired()])
    date = DateField('Fecha de Asistencia', format='%Y-%m-%d', validators=[DataRequired()])
    present = BooleanField('¿Asistió?', default=True)
    submit = SubmitField('Guardar Asistencia')
