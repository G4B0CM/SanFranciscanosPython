from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, IntegerField, TextAreaField, SubmitField, BooleanField,DecimalField
from wtforms.validators import DataRequired, Optional, Length, Email, Regexp, NumberRange,optional
from wtforms.validators import ValidationError
from bson.objectid import ObjectId

def validate_objectid(form, field):
    try:
        ObjectId(str(field.data))
    except Exception:
        raise ValidationError('ID inválido. Debe ser un ObjectId de MongoDB.')

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
    ds_idInstitution = SelectField('Institución (Ficha - Opcional)', choices=[], validators=[Optional()], coerce=str)
    person_id = SelectField('Catequizado', choices=[], validators=[Optional()], coerce=str)
    ds_idCatequizando = IntegerField('ID del Catequizado', validators=[Optional()])
    ds_idCertificate = SelectField('Certificado', choices=[], validators=[Optional()], coerce=str)
    ds_idLevel = SelectField('Nivel de Inscripción (Opcional)', choices=[], validators=[Optional()], coerce=str)
    ds_fechaRegistro = DateField('Fecha de Registro', validators=[DataRequired()])
    ds_schoolsName = StringField('Nombre de la Escuela', validators=[DataRequired(), Length(max=100)])
    ds_schoolGrade = StringField('Grado/Curso Escolar', validators=[DataRequired(), Length(max=30)])

    # --- Padre (Opcionales) ---
    f_firstName = StringField('Primer Nombre del Padre', validators=[Optional(), Length(max=30)])
    f_secondName = StringField('Segundo Nombre del Padre', validators=[Optional(), Length(max=30)])
    f_lastName = StringField('Primer Apellido del Padre', validators=[Optional(), Length(max=30)])
    f_secondLastName = StringField('Segundo Apellido del Padre', validators=[Optional(), Length(max=30)])
    f_ocupation = StringField('Ocupación del Padre', validators=[Optional(), Length(max=50)])
    f_phoneContact = StringField('Teléfono del Padre', validators=[Optional(), Length(max=15), Regexp(r'^\+?1?\d{7,15}$', message="Número inválido.")])
    f_emailContact = StringField('Correo del Padre', validators=[Optional(), Email(), Length(max=100)])

    # --- Madre (Opcionales) ---
    m_firstName = StringField('Primer Nombre de la Madre', validators=[Optional(), Length(max=30)])
    m_secondName = StringField('Segundo Nombre de la Madre', validators=[Optional(), Length(max=30)])
    m_lastName = StringField('Primer Apellido de la Madre', validators=[Optional(), Length(max=30)])
    m_secondLastName = StringField('Segundo Apellido de la Madre', validators=[Optional(), Length(max=30)])
    m_ocupation = StringField('Ocupación de la Madre', validators=[Optional(), Length(max=50)])
    m_phoneContact = StringField('Teléfono de la Madre', validators=[Optional(), Length(max=15), Regexp(r'^\+?1?\d{7,15}$', message="Número inválido.")])
    m_emailContact = StringField('Correo de la Madre', validators=[Optional(), Email(), Length(max=100)])

    # --- Submit ---
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
    type = SelectField(
        'Tipo de Institución',
        choices=[
            ('arquidiocesis', 'Arquidiócesis'),
            ('vicaria', 'Vicaría'),
            ('parroquia', 'Parroquia')
        ],
        validators=[DataRequired()]
    )
    name = StringField('Nombre', validators=[DataRequired(), Length(max=100)])
    address = StringField('Dirección', validators=[Optional(), Length(max=200)])
    phone = StringField('Teléfono', validators=[Optional(), Length(max=20)])
    parish = StringField('Parroquia (si aplica)', validators=[Optional(), Length(max=50)])
    submit = SubmitField('Guardar Institución')

class LevelForm(FlaskForm):
    name = StringField('Nombre del Nivel', validators=[DataRequired(), Length(max=100)])
    description = StringField('Descripción', validators=[DataRequired(), Length(max=200)])
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
    required = BooleanField('¿Es Requisito para Inscribirse a un Nivel?', default=True)
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
        ('Educacion', 'Educacion'),
        ('Sacramentos', 'Sacramentos'),
        ('Salud', 'Salud'),
        ('Legal', 'Legal'),
        ('Otro', 'Otro')
    ], validators=[DataRequired()])
    submit = SubmitField('Guardar Documento')

class CertificateForm(FlaskForm):
    idCatequizado = SelectField("Catequizado", validators=[DataRequired()], coerce=str)
    idSacramento = SelectField("Sacramento", validators=[DataRequired()], coerce=str)
    fechaEmision = DateField("Fecha de Emisión", validators=[DataRequired()])
    lugar = StringField("Lugar", validators=[DataRequired()])
    observaciones = TextAreaField("Observaciones", validators=[Optional()])
    submit = SubmitField("Guardar")

class RolSelectorForm(FlaskForm):
    role = SelectField('Seleccionar Rol', choices=[
        ('', '-- Seleccione un Rol --'),
        ('Catequista', 'Catequista'),
        ('Ayudante', 'Ayudante'),
        ('Eclesiastico', 'Eclesiastico'),
        ('Padrino', 'Padrino'),
        ('PadreMadre', 'Padre/Madre')
    ], validators=[DataRequired()])
    submit = SubmitField('Continuar')

class AttendanceForm(FlaskForm):
    student_id = StringField("ID Catequizado", validators=[DataRequired(), validate_objectid])
    course_id = StringField("ID Curso", validators=[DataRequired(), validate_objectid])
    date = DateField("Fecha", validators=[DataRequired()])
    status = SelectField("Asistió", choices=[("present", "Sí"), ("absent", "No")], validators=[DataRequired()])
    submit = SubmitField("Guardar")

class StudentForm(FlaskForm):
    firstName = StringField('Primer Nombre', validators=[DataRequired(), Length(max=30)])
    secondName = StringField('Segundo Nombre', validators=[Optional(), Length(max=30)])
    lastName = StringField('Primer Apellido', validators=[DataRequired(), Length(max=30)])
    secondLastName = StringField('Segundo Apellido', validators=[Optional(), Length(max=30)])
    sex = SelectField('Sexo', choices=[('', '-- Seleccione --'), ('M', 'Masculino'), ('F', 'Femenino')], validators=[DataRequired()])
    birthdate = DateField('Fecha de Nacimiento', format='%Y-%m-%d', validators=[DataRequired()])
    bloodType = StringField('Tipo de Sangre', validators=[Optional(), Length(max=5)])
    alergies = TextAreaField('Alergias', validators=[Optional(), Length(max=250)])
    emergencyContactName = StringField('Nombre Contacto de Emergencia', validators=[Optional(), Length(max=50)])
    emergencyContactPhone = StringField('Teléfono de Emergencia', validators=[Optional(), Length(max=15), Regexp(r'^\+?1?\d{7,15}$')])
    details = TextAreaField('Detalles Médicos', validators=[Optional(), Length(max=250)])
    submit = SubmitField('Guardar Catequizado')


class PersonForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired(), Length(max=100)])
    surname = StringField('Apellido', validators=[DataRequired(), Length(max=100)])
    document = StringField('Documento de Identidad', validators=[Length(max=30)])
    birthdate = DateField('Fecha de Nacimiento', format='%Y-%m-%d', validators=[DataRequired()])
    
    role = SelectField(
        'Rol',
        choices=[
            ('catequista', 'Catequista'),
            ('ayudante', 'Ayudante'),
            ('eclesiastico', 'Eclesiástico'),
            ('padre', 'Padre'),
            ('madre', 'Madre'),
            ('padrino', 'Padrino'),
            ('otros', 'Otros')
        ],
        validators=[DataRequired()]
    )

    submit = SubmitField('Guardar')
    
class FeBautismalForm(FlaskForm):
    person_id = StringField('ID de Persona', validators=[DataRequired(), validate_objectid])
    church = StringField('Iglesia', validators=[DataRequired()])
    parish_priest = StringField('Párroco')
    date = DateField('Fecha del Bautismo', validators=[DataRequired()])
    submit = SubmitField('Guardar')

class PaymentForm(FlaskForm):
    person_id = StringField('ID de Persona', validators=[DataRequired(), validate_objectid])
    amount = DecimalField('Monto', validators=[DataRequired(), NumberRange(min=0)], places=2)
    method = SelectField('Método de Pago', choices=[
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia'),
        ('tarjeta', 'Tarjeta'),
        ('cheque', 'Cheque'),
        ('otro', 'Otro')
    ], validators=[DataRequired()])
    date = DateField('Fecha de Pago', validators=[DataRequired()])
    notes = StringField('Notas')
    submit = SubmitField('Guardar')