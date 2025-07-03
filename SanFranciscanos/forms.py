from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, IntegerField, TextAreaField, SubmitField, BooleanField, DecimalField
from wtforms.validators import DataRequired, Optional, Length, Email, Regexp, NumberRange

# --- Función de Coerción Personalizada para SelectFields Opcionales ---
def coerce_int_or_none(x):
    """
    Convierte un valor a entero, o a None si está vacío.
    """
    if x == '' or x is None:
        return None
    try:
        return int(x)
    except (ValueError, TypeError):
        return None

# --- Formularios para Roles de Personas (Schema: Persons) ---

class RolSelectorForm(FlaskForm):
    """Formulario para seleccionar el tipo de persona a crear/listar."""
    role = SelectField('Seleccionar Rol', choices=[
        ('', '-- Seleccione un Rol --'),
        ('Catequista', 'Catequista'),
        ('Ayudante', 'Ayudante'),
        ('Eclesiastico', 'Eclesiástico'),
        ('Padrino', 'Padrino'),
        ('PadreMadre', 'Padre/Madre')
    ], validators=[DataRequired()])
    submit = SubmitField('Continuar')

class CatequizadoForm(FlaskForm):
    # Campos de Person
    firstName = StringField('Primer Nombre', validators=[DataRequired(), Length(max=30)])
    secondName = StringField('Segundo Nombre', validators=[Optional(), Length(max=30)])
    lastName = StringField('Primer Apellido', validators=[DataRequired(), Length(max=30)])
    secondLastName = StringField('Segundo Apellido', validators=[Optional(), Length(max=30)])
    sex = SelectField('Sexo', choices=[('M', 'Masculino'), ('F', 'Femenino')], validators=[DataRequired()])
    
    # Campos de Catequizado
    birthdate = DateField('Fecha de Nacimiento', validators=[DataRequired()], format='%Y-%m-%d')
    bloodType = StringField('Tipo de Sangre', validators=[DataRequired(), Length(max=5)])
    emergencyContactName = StringField('Contacto de Emergencia (Nombre)', validators=[DataRequired(), Length(max=50)])
    emergencyContactPhone = StringField('Contacto de Emergencia (Teléfono)', validators=[DataRequired(), Length(max=15)])
    state = BooleanField('Estado Activo', default=True)
    alergies = TextAreaField('Alergias', validators=[Optional()])
    details = TextAreaField('Detalles Adicionales', validators=[Optional()])
    idInstitution = SelectField('Parroquia de Inscripción', coerce=coerce_int_or_none, validators=[Optional()])
    
    submit = SubmitField('Guardar')

class CatequistaForm(FlaskForm):
    """Formulario para Catequista, coincide con sp_InsertCatequista."""
    firstName = StringField('Primer Nombre', validators=[DataRequired(), Length(max=30)])
    secondName = StringField('Segundo Nombre', validators=[Optional(), Length(max=30)])
    lastName = StringField('Primer Apellido', validators=[DataRequired(), Length(max=30)])
    secondLastName = StringField('Segundo Apellido', validators=[Optional(), Length(max=30)])
    sex = SelectField('Sexo', choices=[('', '-- Seleccione --'), ('M', 'Masculino'), ('F', 'Femenino')], validators=[DataRequired()])
    yearsOfExp = IntegerField('Años de experiencia', validators=[DataRequired(), NumberRange(min=0)])
    state = BooleanField('Activo', default=True)
    submit = SubmitField('Guardar Catequista')

class AyudanteForm(FlaskForm):
    """Formulario para Ayudante, coincide con sp_InsertAyudante."""
    firstName = StringField('Primer Nombre', validators=[DataRequired(), Length(max=30)])
    secondName = StringField('Segundo Nombre', validators=[Optional(), Length(max=30)])
    lastName = StringField('Primer Apellido', validators=[DataRequired(), Length(max=30)])
    secondLastName = StringField('Segundo Apellido', validators=[Optional(), Length(max=30)])
    sex = SelectField('Sexo', choices=[('', '-- Seleccione --'), ('M', 'Masculino'), ('F', 'Femenino')], validators=[DataRequired()])
    volunteeringSince = DateField('Voluntario Desde', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Guardar Ayudante')

class EclesiasticoForm(FlaskForm):
    """Formulario para Eclesiastico, coincide con sp_InsertEclesiastico."""
    firstName = StringField('Primer Nombre', validators=[DataRequired(), Length(max=30)])
    secondName = StringField('Segundo Nombre', validators=[Optional(), Length(max=30)])
    lastName = StringField('Primer Apellido', validators=[DataRequired(), Length(max=30)])
    secondLastName = StringField('Segundo Apellido', validators=[Optional(), Length(max=30)])
    sex = SelectField('Sexo', choices=[('', '-- Seleccione --'), ('M', 'Masculino'), ('F', 'Femenino')], validators=[DataRequired()])
    rol = StringField('Rol Eclesiástico', validators=[DataRequired(), Length(max=15)])
    idInstitution = SelectField('Institución Asignada (Opcional)', coerce=coerce_int_or_none, validators=[Optional()])
    state = BooleanField('Activo', default=True)
    submit = SubmitField('Guardar Eclesiástico')

class PadrinoForm(FlaskForm):
    """Formulario para Padrino, coincide con sp_InsertPadrino."""
    firstName = StringField('Primer Nombre', validators=[DataRequired(), Length(max=30)])
    secondName = StringField('Segundo Nombre', validators=[Optional(), Length(max=30)])
    lastName = StringField('Primer Apellido', validators=[DataRequired(), Length(max=30)])
    secondLastName = StringField('Segundo Apellido', validators=[Optional(), Length(max=30)])
    sex = SelectField('Sexo', choices=[('', '-- Seleccione --'), ('M', 'Masculino'), ('F', 'Femenino')], validators=[DataRequired()])
    ocupation = StringField('Ocupación', validators=[DataRequired(), Length(max=50)])
    submit = SubmitField('Guardar Padrino')

class PadreMadreForm(FlaskForm):
    """Formulario para Parent (Padre/Madre), coincide con sp_InsertParent."""
    firstName = StringField('Primer Nombre', validators=[DataRequired(), Length(max=30)])
    secondName = StringField('Segundo Nombre', validators=[Optional(), Length(max=30)])
    lastName = StringField('Primer Apellido', validators=[DataRequired(), Length(max=30)])
    secondLastName = StringField('Segundo Apellido', validators=[Optional(), Length(max=30)])
    sex = SelectField('Sexo', choices=[('', '-- Seleccione --'), ('M', 'Masculino'), ('F', 'Femenino')], validators=[DataRequired()])
    idCatequizado = SelectField('Catequizado Asociado', coerce=coerce_int_or_none, validators=[DataRequired()]) # Se debe poblar dinámicamente
    ocupation = StringField('Ocupación', validators=[DataRequired(), Length(max=50)])
    phoneContact = StringField('Teléfono de Contacto', validators=[DataRequired(), Length(max=15)])
    emailContact = StringField('Correo Electrónico', validators=[DataRequired(), Email(), Length(max=50)])
    submit = SubmitField('Guardar Padre/Madre')

# --- Formularios para Instituciones (Schemas: Institutions) ---

class InstitutionRolSelectorForm(FlaskForm):
    """Formulario para seleccionar el tipo de institución a gestionar."""
    role = SelectField('Tipo de Institución', choices=[
        ('Arquidiocesis', 'Arquidiócesis'),
        ('Vicaria', 'Vicaria'),
        ('Parroquia', 'Parroquia')
    ], validators=[DataRequired()])
    submit = SubmitField('Seleccionar')

class ArquidiocesisForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired(), Length(max=30)])
    mainAddress = StringField('Dirección Principal', validators=[DataRequired(), Length(max=50)])
    city = StringField('Ciudad', validators=[DataRequired(), Length(max=30)])
    # ---#-!-# CORREGIDO ---
    idEclesiastico = SelectField('Eclesiástico Responsable', coerce=coerce_int_or_none, validators=[DataRequired(message="Debe seleccionar un responsable.")])
    submit = SubmitField('Guardar Arquidiócesis')

class VicariaForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired(), Length(max=30)])
    mainAddress = StringField('Dirección Principal', validators=[DataRequired(), Length(max=50)])
    department = StringField('Departamento/Zona Pastoral', validators=[DataRequired(), Length(max=50)])
    # ---#-!-# CORREGIDO ---
    idArquidiocesis = SelectField('Pertenece a la Arquidiócesis', coerce=coerce_int_or_none, validators=[DataRequired(message="Debe seleccionar una arquidiócesis.")])
    idEclesiastico = SelectField('Eclesiástico Responsable (Vicario)', coerce=coerce_int_or_none, validators=[DataRequired(message="Debe seleccionar un responsable.")])
    submit = SubmitField('Guardar Vicaria')

class ParroquiaForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired(), Length(max=30)])
    mainAddress = StringField('Dirección Principal', validators=[DataRequired(), Length(max=50)])
    phone = StringField('Teléfono', validators=[Optional(), Length(max=15)])
    # ---#-!-# CORREGIDO ---
    idVicaria = SelectField('Pertenece a la Vicaria', coerce=coerce_int_or_none, validators=[DataRequired(message="Debe seleccionar una vicaria.")])
    idEclesiastico = SelectField('Eclesiástico Responsable (Párroco)', coerce=coerce_int_or_none, validators=[DataRequired(message="Debe seleccionar un responsable.")])
    submit = SubmitField('Guardar Parroquia')

# --- Formularios para Niveles y Cursos (Schema: Nivel) ---

class LevelRolSelectorForm(FlaskForm):
    """Formulario para seleccionar si gestionar Niveles (definiciones) o Cursos (instancias)."""
    role = SelectField('¿Qué desea gestionar?', choices=[
        ('Level', 'Definiciones de Nivel'),
        ('Curso', 'Cursos Activos')
    ], validators=[DataRequired()])
    submit = SubmitField('Seleccionar')

class LevelForm(FlaskForm):
    idLevel = IntegerField('ID del Nivel (ej: 1, 2, 3)', validators=[DataRequired()])
    name = StringField('Nombre del Nivel', validators=[DataRequired(), Length(max=30)])
    description = TextAreaField('Descripción', validators=[Optional()])
    numberOfOrder = IntegerField('Número de Orden', validators=[Optional()])
    idNextLevel = SelectField('Siguiente Nivel', coerce=coerce_int_or_none, validators=[Optional()])
    idEnabledSacrament = SelectField('Sacramento que Habilita', coerce=coerce_int_or_none, validators=[Optional()])
    submit = SubmitField('Guardar Nivel')

class CursoForm(FlaskForm):
    idLevel = SelectField('Tipo de Nivel', coerce=int, validators=[DataRequired()])
    idParroquia = SelectField('Parroquia donde se imparte', coerce=int, validators=[DataRequired()])
    idCatequista = SelectField('Catequista Principal', coerce=int, validators=[DataRequired()])
    idAyudante = SelectField('Ayudante (Opcional)', coerce=coerce_int_or_none, validators=[Optional()])
    periodYear = IntegerField('Año del Período', validators=[DataRequired()])
    startDate = DateField('Fecha de Inicio', validators=[DataRequired()], format='%Y-%m-%d')
    duration = IntegerField('Duración (en semanas)', validators=[DataRequired()])
    endDate = DateField('Fecha de Fin (Opcional)', validators=[Optional()], format='%Y-%m-%d')
    submit = SubmitField('Guardar Curso')

# --- Formularios para Documentos y Sacramentos (Schemas: Documents, Sacraments) ---

class DocumentRolSelectorForm(FlaskForm):
    role = SelectField('Tipo de Documento a Gestionar', choices=[
        ('DataSheet', 'Ficha de Inscripción Completa'),
        ('Payment', 'Registro de Pago'),
        ('Attendance', 'Registro de Asistencia'),
        ('Acreditation', 'Acreditación de Parroquia'),
        ('BautismFaith', 'Fe de Bautismo'),
        ('LevelAprobation', 'Aprobación de Nivel'),
        ('LevelCertificate', 'Certificado de Nivel')
    ], validators=[DataRequired()])
    submit = SubmitField('Seleccionar')

# El formulario gigante para DataSheet
class DataSheetForm(FlaskForm):
    # Grupo: Datos del Catequizado (c_)
    c_firstName = StringField('Primer Nombre (Catequizado)', validators=[DataRequired()])
    c_secondName = StringField('Segundo Nombre', validators=[Optional()])
    c_lastName = StringField('Primer Apellido', validators=[DataRequired()])
    c_secondLastName = StringField('Segundo Apellido', validators=[Optional()])
    c_sex = SelectField('Sexo', choices=[('M', 'Masculino'), ('F', 'Femenino')], validators=[DataRequired()])
    c_birthdate = DateField('Fecha de Nacimiento', validators=[DataRequired()], format='%Y-%m-%d')
    c_bloodType = StringField('Tipo de Sangre', validators=[DataRequired()])
    c_alergies = TextAreaField('Alergias', validators=[Optional()])
    c_emergencyContactName = StringField('Nombre Contacto de Emergencia', validators=[DataRequired()])
    c_emergencyContactPhone = StringField('Teléfono Contacto de Emergencia', validators=[DataRequired()])
    c_details = TextAreaField('Detalles Médicos Adicionales', validators=[Optional()])
    c_idInstitution = SelectField('Parroquia de Origen (Catequizado)', coerce=coerce_int_or_none, validators=[Optional()])
    
    # Grupo: Datos del Padre (f_) - Opcional
    f_firstName = StringField('Primer Nombre (Padre)', validators=[Optional()])
    f_secondName = StringField('Segundo Nombre (Padre)', validators=[Optional()])
    f_lastName = StringField('Primer Apellido (Padre)', validators=[Optional()])
    f_secondLastName = StringField('Segundo Apellido (Padre)', validators=[Optional()])
    f_ocupation = StringField('Ocupación (Padre)', validators=[Optional()])
    f_phoneContact = StringField('Teléfono (Padre)', validators=[Optional()])
    f_emailContact = StringField('Email (Padre)', validators=[Optional()])
    
    # Grupo: Datos de la Madre (m_) - Opcional
    m_firstName = StringField('Primer Nombre (Madre)', validators=[Optional()])
    m_secondName = StringField('Segundo Nombre (Madre)', validators=[Optional()])
    m_lastName = StringField('Primer Apellido (Madre)', validators=[Optional()])
    m_secondLastName = StringField('Segundo Apellido (Madre)', validators=[Optional()])
    m_ocupation = StringField('Ocupación (Madre)', validators=[Optional()])
    m_phoneContact = StringField('Teléfono (Madre)', validators=[Optional()])
    m_emailContact = StringField('Email (Madre)', validators=[Optional()])

    # Grupo: Datos de la Ficha (ds_)
    ds_sonNumbr = IntegerField('Hijo Número', validators=[Optional()])
    ds_numbrBrothers = IntegerField('Número de Hermanos', validators=[Optional()])
    ds_livesWith = StringField('Vive Con', validators=[Optional()])
    ds_residentialPhone = StringField('Teléfono Residencial', validators=[Optional()])
    ds_mainAddress = TextAreaField('Dirección Principal', validators=[Optional()])
    ds_schoolsName = StringField('Nombre de la Escuela', validators=[DataRequired()])
    ds_schoolGrade = StringField('Grado Escolar', validators=[DataRequired()])
    ds_idInstitution = SelectField('Parroquia donde se inscribe', coerce=coerce_int_or_none, validators=[DataRequired(message="Debe seleccionar la parroquia de inscripción.")])
    ds_idLevel = SelectField('Nivel al que se inscribe', coerce=coerce_int_or_none, validators=[DataRequired(message="Debe seleccionar un nivel.")])

    submit = SubmitField('Crear Ficha de Inscripción')

class PaymentForm(FlaskForm):
    idCatequizado = SelectField('Pago de', coerce=coerce_int_or_none, validators=[DataRequired()])
    amount = DecimalField('Monto', places=2, validators=[DataRequired()])
    paymentMethod = StringField('Método de Pago', validators=[DataRequired()])
    paymentDate = DateField('Fecha de Pago', validators=[DataRequired()], format='%Y-%m-%d')
    paymentState = BooleanField('¿Pagado?', default=True)
    submit = SubmitField('Registrar Pago')

class AttendanceForm(FlaskForm):
    idCurso = SelectField('Curso', coerce=coerce_int_or_none, validators=[DataRequired()])
    idCatequizado = SelectField('Catequizado', coerce=coerce_int_or_none, validators=[DataRequired()])
    dateOfAttendance = DateField('Fecha de Asistencia', validators=[DataRequired()], format='%Y-%m-%d')
    state = BooleanField('Asistió', default=True)
    submit = SubmitField('Guardar Asistencia')

class AcreditationForm(FlaskForm):
    idInstitution = SelectField('Parroquia que Acredita', coerce=coerce_int_or_none, validators=[DataRequired()])
    idCatequizado = SelectField('Acreditar a', coerce=coerce_int_or_none, validators=[DataRequired()])
    messageText = TextAreaField('Mensaje o Contenido de la Acreditación', validators=[DataRequired()])
    submit = SubmitField('Guardar Acreditación')

class BautismFaithForm(FlaskForm):
    idCatequizado = SelectField('Fe de Bautismo de', coerce=coerce_int_or_none, validators=[DataRequired()])
    idParroquia = SelectField('Parroquia del Bautismo', coerce=coerce_int_or_none, validators=[DataRequired()])
    bautismDate = DateField('Fecha de Bautismo', validators=[DataRequired()], format='%Y-%m-%d')
    numbrParroquialRegistration = IntegerField('Número de Registro Parroquial', validators=[DataRequired()])
    idPadre = SelectField('Padre', coerce=coerce_int_or_none, validators=[Optional()])
    idMadre = SelectField('Madre', coerce=coerce_int_or_none, validators=[Optional()])
    idPadrino = SelectField('Padrino/Madrina', coerce=coerce_int_or_none, validators=[Optional()])
    marginalNote = TextAreaField('Nota Marginal', validators=[Optional()])
    submit = SubmitField('Guardar Fe de Bautismo')

class LevelAprobationForm(FlaskForm):
    idCurso = SelectField('Curso', coerce=coerce_int_or_none, validators=[DataRequired()])
    idCatequizado = SelectField('Catequizado', coerce=coerce_int_or_none, validators=[DataRequired()])
    idCatequista = SelectField('Aprobado por Catequista', coerce=coerce_int_or_none, validators=[DataRequired()])
    resultOfLevel = BooleanField('¿Nivel Aprobado?', default=True)
    commentaries = TextAreaField('Comentarios', validators=[Optional()])
    submit = SubmitField('Guardar Aprobación')

class LevelCertificateForm(FlaskForm):
    idCurso = SelectField('Certificado del Curso', coerce=coerce_int_or_none, validators=[DataRequired()])
    idCatequizado = SelectField('Certificado para', coerce=coerce_int_or_none, validators=[DataRequired()])
    idCatequista = SelectField('Emitido por Catequista', coerce=coerce_int_or_none, validators=[DataRequired()])
    idEclesiastico = SelectField('Firmado por Eclesiástico', coerce=coerce_int_or_none, validators=[DataRequired()])
    deliveryDate = DateField('Fecha de Entrega', validators=[DataRequired()], format='%Y-%m-%d')
    catequesisPrhase = StringField('Frase de Catequesis', validators=[Optional()])
    parroquiaLogo = StringField('URL del Logo de la Parroquia', validators=[Optional()])
    commentaries = TextAreaField('Comentarios Adicionales', validators=[Optional()])
    submit = SubmitField('Generar Certificado')

# --- Formularios para Sacramentos y Asignaciones (Schemas: Sacraments) ---

class SacramentRolSelectorForm(FlaskForm):
    """Formulario para seleccionar si gestionar Sacramentos o Asignaciones."""
    role = SelectField('¿Qué desea gestionar?', choices=[
        ('Sacrament', 'Eventos de Sacramento'),
        ('CatequizadoSacramento', 'Asignaciones de Sacramentos')
    ], validators=[DataRequired()])
    submit = SubmitField('Seleccionar')

class SacramentForm(FlaskForm):
    idSacrament = IntegerField('ID del Sacramento (ej: 101, 102)', validators=[DataRequired()])
    type = StringField('Tipo de Sacramento (ej: Confirmación, Comunión)', validators=[DataRequired(), Length(max=50)])
    celebrationDate = DateField('Fecha de Celebración', validators=[DataRequired()], format='%Y-%m-%d')
    # ---#-!-# CORREGIDO ---
    idInstitution = SelectField('Parroquia donde se celebra', coerce=coerce_int_or_none, validators=[DataRequired(message="Debe seleccionar una parroquia.")])
    observations = TextAreaField('Observaciones', validators=[Optional()])
    submit = SubmitField('Guardar Sacramento')

class CatequizadoSacramentoForm(FlaskForm):
    # ---#-!-# CORREGIDO ---
    idSacramento = SelectField('Seleccionar Sacramento/Evento', coerce=coerce_int_or_none, validators=[DataRequired(message="Debe seleccionar un evento.")])
    idCatequizado = SelectField('Seleccionar Catequizado', coerce=coerce_int_or_none, validators=[DataRequired(message="Debe seleccionar un catequizado.")])
    # Este ya estaba bien, pero lo dejamos para consistencia
    idPadrino = SelectField('Seleccionar Padrino/Madrina (Opcional)', coerce=coerce_int_or_none, validators=[Optional()])
    submit = SubmitField('Asignar Sacramento')

# --- Formularios Auxiliares ---

class DeleteForm(FlaskForm):
    """Formulario vacío para el botón de eliminar, solo para protección CSRF."""
    submit = SubmitField('Eliminar')