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
    idCatequizado = SelectField('Catequizado Asociado', coerce=int, validators=[DataRequired()]) # Se debe poblar dinámicamente
    ocupation = StringField('Ocupación', validators=[DataRequired(), Length(max=50)])
    phoneContact = StringField('Teléfono de Contacto', validators=[DataRequired(), Length(max=15)])
    emailContact = StringField('Correo Electrónico', validators=[DataRequired(), Email(), Length(max=50)])
    submit = SubmitField('Guardar Padre/Madre')

# --- Formularios para Entidades de Instituciones (Schema: Institutions) ---

class ArquidiocesisForm(FlaskForm):
    """Formulario para Arquidiocesis, coincide con sp_InsertArquidiocesis."""
    name = StringField('Nombre', validators=[DataRequired(), Length(max=30)])
    mainAddress = StringField('Dirección', validators=[DataRequired(), Length(max=50)])
    type = StringField('Tipo', default='Arquidiocesis', render_kw={'readonly': True})
    city = StringField('Ciudad', validators=[DataRequired(), Length(max=30)])
    idEclesiastico = SelectField('Eclesiástico a Cargo', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Guardar Arquidiócesis')

class VicariaForm(FlaskForm):
    """Formulario para Vicaria, coincide con sp_InsertVicaria."""
    name = StringField('Nombre', validators=[DataRequired(), Length(max=30)])
    mainAddress = StringField('Dirección', validators=[DataRequired(), Length(max=50)])
    type = StringField('Tipo', default='Vicaria', render_kw={'readonly': True})
    department = StringField('Departamento/Zona Pastoral', validators=[DataRequired(), Length(max=50)])
    idArquidiocesis = SelectField('Arquidiócesis a la que Pertenece', coerce=int, validators=[DataRequired()])
    idEclesiastico = SelectField('Vicario a Cargo', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Guardar Vicaria')

class ParroquiaForm(FlaskForm):
    """Formulario para Parroquia, coincide con sp_InsertParroquia."""
    name = StringField('Nombre', validators=[DataRequired(), Length(max=30)])
    mainAddress = StringField('Dirección', validators=[DataRequired(), Length(max=50)])
    type = StringField('Tipo', default='Parroquia', render_kw={'readonly': True})
    phone = StringField('Teléfono', validators=[Optional(), Length(max=15)])
    idVicaria = SelectField('Vicaria a la que Pertenece', coerce=int, validators=[DataRequired()])
    idEclesiastico = SelectField('Párroco a Cargo', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Guardar Parroquia')

# --- Formularios para Niveles y Cursos (Schema: Nivel) ---

class LevelForm(FlaskForm):
    """Formulario para Level, coincide con sp_InsertLevel."""
    idLevel = IntegerField('ID del Nivel', validators=[DataRequired()]) # PK, no identity
    name = StringField('Nombre del Nivel', validators=[DataRequired(), Length(max=30)])
    description = TextAreaField('Descripción (Opcional)', validators=[Optional()])
    idNextLevel = SelectField('Siguiente Nivel (Opcional)', coerce=coerce_int_or_none, validators=[Optional()])
    numberOfOrder = IntegerField('Número de Orden', validators=[DataRequired(), NumberRange(min=1)])
    idEnabledSacrament = SelectField('Sacramento que Habilita (Opcional)', coerce=coerce_int_or_none, validators=[Optional()])
    submit = SubmitField('Guardar Nivel')
    
class CursoForm(FlaskForm):
    """Formulario para Curso, coincide con sp_InsertCurso."""
    idLevel = SelectField('Tipo de Nivel', coerce=int, validators=[DataRequired()])
    idParroquia = SelectField('Parroquia donde se imparte', coerce=int, validators=[DataRequired()])
    idCatequista = SelectField('Catequista Principal', coerce=int, validators=[DataRequired()])
    idAyudante = SelectField('Ayudante de Apoyo (Opcional)', coerce=coerce_int_or_none, validators=[Optional()])
    periodYear = IntegerField('Año del Periodo (Ej: 2024)', validators=[DataRequired(), NumberRange(min=2000, max=2100)])
    startDate = DateField('Fecha de Inicio', format='%Y-%m-%d', validators=[DataRequired()])
    duration = IntegerField('Duración (en semanas)', validators=[DataRequired(), NumberRange(min=1)])
    endDate = DateField('Fecha de Fin (Opcional)', format='%Y-%m-%d', validators=[Optional()])
    submit = SubmitField('Guardar Curso')

class GruposForm(FlaskForm):
    """Formulario para inscribir un catequizado en un curso."""
    idCurso = SelectField('Seleccionar Curso', coerce=int, validators=[DataRequired()])
    idCatequizado = SelectField('Seleccionar Catequizado', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Inscribir en Grupo')

# --- Formularios para Documentos y Sacramentos (Schemas: Documents, Sacraments) ---

class DataSheetForm(FlaskForm):
    """Formulario complejo para la Hoja de Datos, coincide con sp_InsertDataSheet."""
    # Catequizado (Person)
    c_firstName = StringField('Primer Nombre (Catequizado)', validators=[DataRequired(), Length(max=30)])
    c_secondName = StringField('Segundo Nombre', validators=[Optional(), Length(max=30)])
    c_lastName = StringField('Primer Apellido', validators=[DataRequired(), Length(max=30)])
    c_secondLastName = StringField('Segundo Apellido', validators=[Optional(), Length(max=30)])
    c_sex = SelectField('Sexo', choices=[('', '-- Seleccione --'), ('M', 'Masculino'), ('F', 'Femenino')], validators=[DataRequired()])
    # DataSheet (specific)
    ds_sonNumbr = IntegerField('Hijo Número', validators=[Optional(), NumberRange(min=0)])
    ds_numbrBrothers = IntegerField('Número de Hermanos', validators=[Optional(), NumberRange(min=0)])
    ds_livesWith = StringField('Vive Con', validators=[Optional(), Length(max=50)])
    ds_residentialPhone = StringField('Teléfono Residencial', validators=[Optional(), Length(max=15)])
    ds_mainAddress = TextAreaField('Dirección', validators=[Optional(), Length(max=150)])
    # Catequizado (specific)
    c_birthdate = DateField('Fecha de Nacimiento', format='%Y-%m-%d', validators=[DataRequired()])
    c_bloodType = StringField('Tipo de Sangre', validators=[DataRequired(), Length(max=5)])
    c_alergies = TextAreaField('Alergias', validators=[Optional()])
    c_emergencyContactName = StringField('Contacto de Emergencia', validators=[DataRequired(), Length(max=50)])
    c_emergencyContactPhone = StringField('Teléfono de Emergencia', validators=[DataRequired(), Length(max=15)])
    c_details = TextAreaField('Detalles Adicionales', validators=[Optional()])
    c_idInstitution = SelectField('Parroquia (Catequizado)', coerce=coerce_int_or_none, validators=[Optional()])
    # Padre (Person + Parent)
    f_firstName = StringField('Primer Nombre (Padre)', validators=[Optional(), Length(max=30)])
    f_secondName = StringField('Segundo Nombre (Padre)', validators=[Optional(), Length(max=30)])
    f_lastName = StringField('Primer Apellido (Padre)', validators=[Optional(), Length(max=30)])
    f_secondLastName = StringField('Segundo Apellido (Padre)', validators=[Optional(), Length(max=30)])
    f_ocupation = StringField('Ocupación (Padre)', validators=[Optional(), Length(max=50)])
    f_phoneContact = StringField('Teléfono (Padre)', validators=[Optional(), Length(max=15)])
    f_emailContact = StringField('Email (Padre)', validators=[Optional(), Email(), Length(max=50)])
    # Madre (Person + Parent)
    m_firstName = StringField('Primer Nombre (Madre)', validators=[Optional(), Length(max=30)])
    m_secondName = StringField('Segundo Nombre (Madre)', validators=[Optional(), Length(max=30)])
    m_lastName = StringField('Primer Apellido (Madre)', validators=[Optional(), Length(max=30)])
    m_secondLastName = StringField('Segundo Apellido (Madre)', validators=[Optional(), Length(max=30)])
    m_ocupation = StringField('Ocupación (Madre)', validators=[Optional(), Length(max=50)])
    m_phoneContact = StringField('Teléfono (Madre)', validators=[Optional(), Length(max=15)])
    m_emailContact = StringField('Email (Madre)', validators=[Optional(), Email(), Length(max=50)])
    # DataSheet (IDs y Escolar)
    ds_idInstitution = SelectField('Institución (Ficha)', coerce=coerce_int_or_none, validators=[Optional()])
    ds_idCertificate = IntegerField('ID Certificado (Opcional)', validators=[Optional()])
    ds_idLevel = SelectField('Nivel (Ficha)', coerce=coerce_int_or_none, validators=[Optional()])
    ds_schoolsName = StringField('Nombre de la Escuela', validators=[DataRequired(), Length(max=100)])
    ds_schoolGrade = StringField('Grado/Curso Escolar', validators=[DataRequired(), Length(max=30)])
    submit = SubmitField('Guardar Hoja de Datos')

class SacramentForm(FlaskForm):
    """Formulario para Sacrament, coincide con sp_InsertSacrament."""
    idSacrament = IntegerField('ID Sacramento', validators=[DataRequired()]) # PK, no identity
    celebrationDate = DateField('Fecha de Celebración', format='%Y-%m-%d', validators=[DataRequired()])
    observations = TextAreaField('Observaciones', validators=[DataRequired()])
    type = StringField('Tipo de Sacramento', validators=[DataRequired(), Length(max=50)])
    idInstitution = SelectField('Parroquia de Celebración', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Guardar Sacramento')

# --- Formularios Auxiliares ---

class DeleteForm(FlaskForm):
    """Formulario vacío para el botón de eliminar, solo para protección CSRF."""
    submit = SubmitField('Eliminar')