import decimal
from typing import List, Optional

from sqlalchemy import Boolean, CHAR, Column, Date, ForeignKey, ForeignKeyConstraint, Identity, Index, Integer, PrimaryKeyConstraint, Table, Unicode, DECIMAL, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import datetime

class Base(DeclarativeBase):
    pass

# --- Esquema Persons ---

class Person(Base):
    __tablename__ = 'Person'
    __table_args__ = (
        PrimaryKeyConstraint('idPerson', name='Person_PK'),
        Index('PersonFirstName_IDX', 'firstName'),
        Index('PersonLastName_IDX', 'lastName'), # Corregido: lastName en lugar de lastName
        {'schema': 'Persons'}
    )

    idPerson: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True)
    firstName: Mapped[Optional[str]] = mapped_column(Unicode(30)) # Removida collation para simplificar, SQL Server usará la de la BD o columna
    secondName: Mapped[Optional[str]] = mapped_column(Unicode(30))
    lastName: Mapped[Optional[str]] = mapped_column(Unicode(30))
    secondLastName: Mapped[Optional[str]] = mapped_column(Unicode(30))
    sex: Mapped[Optional[str]] = mapped_column(CHAR(1))

    parents_representing: Mapped[List['Parent']] = relationship('Parent', back_populates='person_record', foreign_keys='Parent.idPerson')


class Parent(Base): 
    __tablename__ = 'Parent' 
    __table_args__ = (
        # ForeignKeyConstraint(['idCatequizado'], ['Persons.Catequizado.idPerson'], name='ParentCatequizado_FK'), # Parent se vincula a Catequizado, no a Person directamente
        PrimaryKeyConstraint('idPerson', name='Parent_PK'), # idPerson aquí es el ID de la persona que ES el padre/madre
        {'schema': 'Persons'}
    )

    idPerson: Mapped[int] = mapped_column(Integer, ForeignKey('Persons.Person.idPerson'), primary_key=True) # Este es el ID de la persona que es padre/madre
    idCatequizado: Mapped[int] = mapped_column(Integer, ForeignKey('Persons.Catequizado.idPerson'), index=True) # A qué catequizado representa
    ocupation: Mapped[str] = mapped_column(Unicode(50))
    phoneContact: Mapped[str] = mapped_column(Unicode(15))
    emailContact: Mapped[str] = mapped_column(Unicode(50))

    # Relación Muchos a Uno: Este registro de Parent se refiere a una Person (el padre/madre)
    person_record: Mapped['Person'] = relationship('Person', back_populates='parents_representing', foreign_keys=[idPerson])
    # Relación Muchos a Uno: Este registro de Parent se refiere a un Catequizado (el hijo/a)
    catequizado_represented: Mapped['Catequizado'] = relationship('Catequizado', back_populates='parent_records_datasheet_papa', foreign_keys=[idCatequizado],
                                                                 primaryjoin="Parent.idCatequizado == Catequizado.idPerson") # Ajustar primaryjoin si es necesario

    # Relaciones para BautismFaith
    # Si un padre/madre puede estar en múltiples BautismFaith (como padre y como madre)
    bautismos_como_padre: Mapped[List['BautismFaith']] = relationship('BautismFaith', foreign_keys='BautismFaith.idPadre', back_populates='padre_record')
    bautismos_como_madre: Mapped[List['BautismFaith']] = relationship('BautismFaith', foreign_keys='BautismFaith.idMadre', back_populates='madre_record')

    # Relaciones para DataSheet
    datasheets_como_papa: Mapped[List['DataSheet']] = relationship('DataSheet', foreign_keys='DataSheet.idPapa', back_populates='papa_record')
    datasheets_como_mama: Mapped[List['DataSheet']] = relationship('DataSheet', foreign_keys='DataSheet.idMama', back_populates='mama_record')

# --- Subclases de Person (Herencia Unida) ---

class Catequizado(Person):
    __tablename__ = 'Catequizado'
    __table_args__ = (
        ForeignKeyConstraint(['idPerson'], ['Persons.Person.idPerson'], name='CatequizadoPerson_FK'),
        ForeignKeyConstraint(['idInstitution'], ['Institutions.Parroquia.idInstitution'], name='CatequizadoParroquia_FK'), # Parroquia donde se inscribe/pertenece
        PrimaryKeyConstraint('idPerson', name='Catequizado_PK'),
        {'schema': 'Persons'}
    )

    idPerson: Mapped[int] = mapped_column(Integer, ForeignKey('Persons.Person.idPerson'), primary_key=True)
    birthdate: Mapped[datetime.date] = mapped_column(Date)
    bloodType: Mapped[str] = mapped_column(Unicode(5))
    emergencyContactName: Mapped[str] = mapped_column(Unicode(50)) # Ajustada longitud
    emergencyContactPhone: Mapped[str] = mapped_column(Unicode(15))
    state: Mapped[bool] = mapped_column(Boolean)
    alergies: Mapped[Optional[str]] = mapped_column(Text) # Usar Text para NVARCHAR(MAX)
    details: Mapped[Optional[str]] = mapped_column(Text)
    idInstitution: Mapped[Optional[int]] = mapped_column(Integer) # FK a Parroquia

    # Relación con Parroquia
    parroquia_inscrito: Mapped[Optional['Parroquia']] = relationship('Parroquia', back_populates='catequizados_en_parroquia', foreign_keys=[idInstitution])

    # Relaciones (propiedades que tenía tu código original, las estoy conectando)
    acreditaciones: Mapped[List['Acreditation']] = relationship('Acreditation', back_populates='catequizado_acreditado', foreign_keys='Acreditation.idCatequizado')
    fe_bautismo: Mapped[List['BautismFaith']] = relationship('BautismFaith', back_populates='catequizado_bautizado', foreign_keys='BautismFaith.idCatequizado') # Un catequizado usualmente tiene una fe de bautismo
    fichas_datos: Mapped[List['DataSheet']] = relationship('DataSheet', back_populates='catequizado_en_ficha', foreign_keys='DataSheet.idCatequizado')
    autorizaciones_parroco: Mapped[List['ParrocoAuth']] = relationship('ParrocoAuth', back_populates='catequizado_autorizado', foreign_keys='ParrocoAuth.idCatequizado')
    pagos_realizados: Mapped[List['Payment']] = relationship('Payment', back_populates='catequizado_del_pago', foreign_keys='Payment.idCatequizado')

    asistencias: Mapped[List['Attendance']] = relationship('Attendance', back_populates='catequizado_asistente', foreign_keys='Attendance.idCatequizado')
    aprobaciones_nivel: Mapped[List['LevelAprobation']] = relationship('LevelAprobation', back_populates='catequizado_aprobado', foreign_keys='LevelAprobation.idCatequizado')
    certificados_nivel: Mapped[List['LevelCertificate']] = relationship('LevelCertificate', back_populates='catequizado_certificado', foreign_keys='LevelCertificate.idCatequizado')

    sacramentos_recibidos: Mapped[List['CatequizadoSacramento']] = relationship('CatequizadoSacramento', back_populates='catequizado_que_recibe', foreign_keys='CatequizadoSacramento.idCatequizado')
    
    # Relación con Parent (para acceder a los registros de padre/madre desde el catequizado)
    # Un catequizado puede tener registros de padre y madre en la tabla Parent.
    # Esta es una forma, otra es a través de DataSheet o BautismFaith si solo se necesitan en ese contexto.
    parent_records_datasheet_papa: Mapped[List['Parent']] = relationship(
        'Parent',
        foreign_keys='Parent.idCatequizado',
        primaryjoin="and_(Parent.idCatequizado == Catequizado.idPerson)", # Asegúrate que el join sea correcto
        back_populates='catequizado_represented'
        # podrías necesitar primaryjoin más específicos si hay varios roles de Parent para un Catequizado
    )


    # Relación Muchos a Muchos con Curso a través de la tabla Grupos
    cursos_inscrito: Mapped[List['Curso']] = relationship(
        'Curso',
        secondary='Nivel.Grupos', # Nombre de la tabla de asociación con esquema
        back_populates='catequizados_inscritos'
    )

    __mapper_args__ = {
        'polymorphic_identity': 'catequizado', # Necesario si Person tuviera una columna 'type' para polimorfismo
        'inherit_condition': idPerson == Person.idPerson # Condición para la herencia unida
    }


class Ayudante(Person):
    __tablename__ = 'Ayudante'
    __table_args__ = (
        ForeignKeyConstraint(['idPerson'], ['Persons.Person.idPerson'], name='AyudantePerson_FK'),
        PrimaryKeyConstraint('idPerson', name='Ayudante_PK'),
        {'schema': 'Persons'}
    )

    idPerson: Mapped[int] = mapped_column(Integer, ForeignKey('Persons.Person.idPerson'), primary_key=True)
    volunteeringSince: Mapped[datetime.date] = mapped_column(Date)
    # La relación idLevel, periodYear, startDate, endDate estaba en tu BD original en Ayudante
    # Si un ayudante está asignado a un curso específico:
    # idCurso: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('Nivel.Curso.idCurso')) # O idAyudante en Curso
    
    cursos_como_ayudante: Mapped[List['Curso']] = relationship('Curso', back_populates='ayudante_asignado', foreign_keys='Curso.idAyudante')


    __mapper_args__ = {
        'polymorphic_identity': 'ayudante',
        'inherit_condition': idPerson == Person.idPerson
    }


class Catequista(Person):
    __tablename__ = 'Catequista'
    __table_args__ = (
        ForeignKeyConstraint(['idPerson'], ['Persons.Person.idPerson'], name='CatequistaPerson_FK'),
        PrimaryKeyConstraint('idPerson', name='Catequista_PK'),
        {'schema': 'Persons'}
    )

    idPerson: Mapped[int] = mapped_column(Integer, ForeignKey('Persons.Person.idPerson'), primary_key=True)
    yearsOfExp: Mapped[int] = mapped_column(Integer)
    state: Mapped[bool] = mapped_column(Boolean)

    # Relaciones
    cursos_asignados: Mapped[List['Curso']] = relationship('Curso', back_populates='catequista_principal', foreign_keys='Curso.idCatequista')
    asistencias_tomadas: Mapped[List['Attendance']] = relationship('Attendance', back_populates='catequista_que_registra', foreign_keys='Attendance.idCatequista')
    aprobaciones_emitidas: Mapped[List['LevelAprobation']] = relationship('LevelAprobation', back_populates='catequista_que_aprueba', foreign_keys='LevelAprobation.idCatequista')
    certificados_emitidos: Mapped[List['LevelCertificate']] = relationship('LevelCertificate', back_populates='catequista_que_certifica', foreign_keys='LevelCertificate.idCatequista')

    __mapper_args__ = {
        'polymorphic_identity': 'catequista',
        'inherit_condition': idPerson == Person.idPerson
    }


class Eclesiastico(Person):
    __tablename__ = 'Eclesiastico'
    __table_args__ = (
        ForeignKeyConstraint(['idPerson'], ['Persons.Person.idPerson'], name='EclesiasticoPerson_FK'),
        ForeignKeyConstraint(['idInstitution'], ['Institutions.Institution.idInstitution'], name='EclesiasticoInstitution_FK'), # Institución donde sirve
        PrimaryKeyConstraint('idPerson', name='Eclesiastico_PK'),
        {'schema': 'Persons'}
    )

    idPerson: Mapped[int] = mapped_column(Integer, ForeignKey('Persons.Person.idPerson'), primary_key=True)
    rol: Mapped[str] = mapped_column(Unicode(15))
    state: Mapped[bool] = mapped_column(Boolean)
    idInstitution: Mapped[Optional[int]] = mapped_column(Integer) # FK a Institution

    # Relación con Institution
    institucion_asignada: Mapped[Optional['Institution']] = relationship('Institution', back_populates='eclesiasticos_en_institucion', foreign_keys=[idInstitution])
    
    # Si un eclesiástico firma certificados
    certificados_firmados: Mapped[List['LevelCertificate']] = relationship('LevelCertificate', back_populates='eclesiastico_que_firma', foreign_keys='LevelCertificate.idEclesiastico')


    __mapper_args__ = {
        'polymorphic_identity': 'eclesiastico',
        'inherit_condition': idPerson == Person.idPerson
    }


class Padrino(Person):
    __tablename__ = 'Padrino'
    __table_args__ = (
        ForeignKeyConstraint(['idPerson'], ['Persons.Person.idPerson'], name='PadrinoPerson_FK'),
        PrimaryKeyConstraint('idPerson', name='Padrino_PK'),
        {'schema': 'Persons'}
    )

    idPerson: Mapped[int] = mapped_column(Integer, ForeignKey('Persons.Person.idPerson'), primary_key=True)
    ocupation: Mapped[str] = mapped_column(Unicode(50))

    # Relaciones
    sacramentos_apadrinados: Mapped[List['CatequizadoSacramento']] = relationship('CatequizadoSacramento', back_populates='padrino_del_sacramento', foreign_keys='CatequizadoSacramento.idPadrino')
    bautismos_apadrinados: Mapped[List['BautismFaith']] = relationship('BautismFaith', back_populates='padrino_del_bautismo', foreign_keys='BautismFaith.idPadrino')


    __mapper_args__ = {
        'polymorphic_identity': 'padrino',
        'inherit_condition': idPerson == Person.idPerson
    }

# --- Esquema Institutions ---

class Institution(Base):
    __tablename__ = 'Institution'
    __table_args__ = (
        # ForeignKeyConstraint(['idEclesiastico'], ['Persons.Eclesiastico.idPerson'], name='InstitutionEclesiastico_FK'), # Un eclesiástico principal
        PrimaryKeyConstraint('idInstitution', name='Institution_PK'),
        {'schema': 'Institutions'}
    )

    idInstitution: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True)
    name: Mapped[str] = mapped_column(Unicode(30))
    mainAddress: Mapped[str] = mapped_column(Unicode(50)) # Cambiado de 'address' en tu BD original
    type: Mapped[str] = mapped_column(Unicode(30)) # Ej: 'Parroquia', 'Arquidiocesis', 'Vicaria'
    # idEclesiastico: Mapped[Optional[int]] = mapped_column(Integer) # FK a Eclesiastico (responsable principal)

    # Relación con Eclesiastico (muchos eclesiásticos pueden pertenecer a una institución)
    eclesiasticos_en_institucion: Mapped[List['Eclesiastico']] = relationship('Eclesiastico', back_populates='institucion_asignada', foreign_keys='Eclesiastico.idInstitution')

    # Relación con BautismFaith (si la institución es la parroquia del bautismo)
    bautismos_realizados_aqui: Mapped[List['BautismFaith']] = relationship('BautismFaith', back_populates='parroquia_bautismo', foreign_keys='BautismFaith.idParroquia')
    # Relación con DataSheet (si la institución es relevante para la ficha)
    fichas_datos_institucion: Mapped[List['DataSheet']] = relationship('DataSheet', back_populates='institucion_ficha', foreign_keys='DataSheet.idInstitution')
    # Relación con Curso (la institución donde se da el curso, usualmente una parroquia)
    cursos_impartidos_aqui: Mapped[List['Curso']] = relationship('Curso', back_populates='parroquia_del_curso', foreign_keys='Curso.idParroquia')


class Arquidiocesis(Institution):
    __tablename__ = 'Arquidiocesis'
    __table_args__ = (
        ForeignKeyConstraint(['idInstitution'], ['Institutions.Institution.idInstitution'], name='ArquidiocesisInstitution_FK'),
        PrimaryKeyConstraint('idInstitution', name='Arquidiocesis_PK'),
        {'schema': 'Institutions'}
    )
    idInstitution: Mapped[int] = mapped_column(Integer, ForeignKey('Institutions.Institution.idInstitution'), primary_key=True)
    city: Mapped[str] = mapped_column(Unicode(30))

    vicarias_en_arquidiocesis: Mapped[List['Vicaria']] = relationship('Vicaria', back_populates='arquidiocesis_pertenece', foreign_keys='Vicaria.idArquidiocesis')

    __mapper_args__ = {'polymorphic_identity': 'arquidiocesis'}


class Vicaria(Institution):
    __tablename__ = 'Vicaria'
    __table_args__ = (
        ForeignKeyConstraint(['idInstitution'], ['Institutions.Institution.idInstitution'], name='VicariaInstitution_FK'),
        ForeignKeyConstraint(['idArquidiocesis'], ['Institutions.Arquidiocesis.idInstitution'], name='VicariaArquidiocesis_FK'),
        PrimaryKeyConstraint('idInstitution', name='Vicaria_PK'),
        Index('VicariaArquidiocesis_IDX', 'idArquidiocesis'),
        {'schema': 'Institutions'}
    )
    idInstitution: Mapped[int] = mapped_column(Integer, ForeignKey('Institutions.Institution.idInstitution'), primary_key=True)
    department: Mapped[str] = mapped_column(Unicode(50))
    idArquidiocesis: Mapped[int] = mapped_column(Integer) # FK a Arquidiocesis

    arquidiocesis_pertenece: Mapped['Arquidiocesis'] = relationship('Arquidiocesis', back_populates='vicarias_en_arquidiocesis', foreign_keys=[idArquidiocesis])
    parroquias_en_vicaria: Mapped[List['Parroquia']] = relationship('Parroquia', back_populates='vicaria_pertenece', foreign_keys='Parroquia.idVicaria')

    __mapper_args__ = {'polymorphic_identity': 'vicaria'}


class Parroquia(Institution):
    __tablename__ = 'Parroquia'
    __table_args__ = (
        ForeignKeyConstraint(['idInstitution'], ['Institutions.Institution.idInstitution'], name='ParroquiaInstitution_FK'),
        ForeignKeyConstraint(['idVicaria'], ['Institutions.Vicaria.idInstitution'], name='ParroquiaVicaria_FK'),
        PrimaryKeyConstraint('idInstitution', name='Parroquia_PK'),
        Index('ParroquiaVicaria_IDX', 'idVicaria'),
        {'schema': 'Institutions'}
    )
    idInstitution: Mapped[int] = mapped_column(Integer, ForeignKey('Institutions.Institution.idInstitution'), primary_key=True)
    idVicaria: Mapped[int] = mapped_column(Integer) # FK a Vicaria
    phone: Mapped[Optional[str]] = mapped_column(Unicode(15))

    vicaria_pertenece: Mapped['Vicaria'] = relationship('Vicaria', back_populates='parroquias_en_vicaria', foreign_keys=[idVicaria])
    
    # Relaciones que Parroquia "provee" o "contiene"
    catequizados_en_parroquia: Mapped[List['Catequizado']] = relationship('Catequizado', back_populates='parroquia_inscrito', foreign_keys='Catequizado.idInstitution')
    acreditaciones_emitidas: Mapped[List['Acreditation']] = relationship('Acreditation', back_populates='parroquia_que_acredita', foreign_keys='Acreditation.idInstitution')
    autorizaciones_emitidas: Mapped[List['ParrocoAuth']] = relationship('ParrocoAuth', back_populates='parroquia_que_autoriza', foreign_keys='ParrocoAuth.idParroquia')
    sacramentos_celebrados_aqui: Mapped[List['Sacrament']] = relationship('Sacrament', back_populates='parroquia_celebracion', foreign_keys='Sacrament.idInstitution')

    __mapper_args__ = {'polymorphic_identity': 'parroquia'}


# --- Esquema Documents (Tablas independientes) ---

class Document(Base): # Si todavía necesitas una tabla Document base para algunos tipos de documentos
    __tablename__ = 'Document'
    __table_args__ = (
        PrimaryKeyConstraint('idDocument', name='Document_PK'),
        {'schema': 'Documents'}
    )
    idDocument: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True)
    emissionDate: Mapped[datetime.date] = mapped_column(Date)
    idEmisor: Mapped[int] = mapped_column(Integer) # Podría ser FK a Person o Institution
    idReceptor: Mapped[int] = mapped_column(Integer) # Podría ser FK a Person o Institution
    type: Mapped[str] = mapped_column(Unicode(20))
    numberDocument: Mapped[int] = mapped_column(Integer)

    # Relación a ParrocoAuth si hereda
    parroco_auth_detail: Mapped[Optional['ParrocoAuth']] = relationship('ParrocoAuth', back_populates='document_base', uselist=False)


class Acreditation(Base):
    __tablename__ = 'Acreditation'
    __table_args__ = (
        ForeignKeyConstraint(['idCatequizado'], ['Persons.Catequizado.idPerson'], name='AcreditationCatequizado_FK'),
        ForeignKeyConstraint(['idInstitution'], ['Institutions.Parroquia.idInstitution'], name='AcreditationParroquia_FK'), # Parroquia que acredita
        PrimaryKeyConstraint('idAcreditation', name='Acreditation_PK'),
        Index('AcreditationCatequizado_IDX', 'idCatequizado'),
        {'schema': 'Documents'}
    )
    idAcreditation: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True)
    idInstitution: Mapped[int] = mapped_column(Integer) # FK a Parroquia
    idCatequizado: Mapped[int] = mapped_column(Integer) # FK a Catequizado
    messageText: Mapped[Optional[str]] = mapped_column(Text)

    catequizado_acreditado: Mapped['Catequizado'] = relationship('Catequizado', back_populates='acreditaciones', foreign_keys=[idCatequizado])
    parroquia_que_acredita: Mapped['Parroquia'] = relationship('Parroquia', back_populates='acreditaciones_emitidas', foreign_keys=[idInstitution])


class BautismFaith(Base):
    __tablename__ = 'BautismFaith'
    __table_args__ = (
        ForeignKeyConstraint(['idCatequizado'], ['Persons.Catequizado.idPerson'], name='BautismFaithCatequizado_FK'),
        ForeignKeyConstraint(['idMadre'], ['Persons.Parent.idPerson'], name='BautismFaithMadre_FK'),
        ForeignKeyConstraint(['idPadre'], ['Persons.Parent.idPerson'], name='BautismFaithPadre_FK'),
        ForeignKeyConstraint(['idPadrino'], ['Persons.Padrino.idPerson'], name='BautismFaithPadrino_FK'),
        ForeignKeyConstraint(['idParroquia'], ['Institutions.Institution.idInstitution'], name='BautismFaithParroquia_FK'), # Parroquia donde se bautizó
        PrimaryKeyConstraint('idBautismFaith', name='BautismFaith_PK'),
        {'schema': 'Documents'}
    )
    idBautismFaith: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True)
    bautismDate: Mapped[datetime.date] = mapped_column(Date)
    numbrParroquialRegistration: Mapped[int] = mapped_column(Integer) # Corregido nombre
    idCatequizado: Mapped[int] = mapped_column(Integer) # FK a Catequizado
    idParroquia: Mapped[int] = mapped_column(Integer)   # FK a Institution (Parroquia)
    idPadre: Mapped[Optional[int]] = mapped_column(Integer)     # FK a Parent
    idMadre: Mapped[Optional[int]] = mapped_column(Integer)     # FK a Parent
    idPadrino: Mapped[Optional[int]] = mapped_column(Integer)   # FK a Padrino
    marginalNote: Mapped[Optional[str]] = mapped_column(Text)

    catequizado_bautizado: Mapped['Catequizado'] = relationship('Catequizado', back_populates='fe_bautismo', foreign_keys=[idCatequizado])
    parroquia_bautismo: Mapped['Institution'] = relationship('Institution', back_populates='bautismos_realizados_aqui', foreign_keys=[idParroquia])
    padre_record: Mapped[Optional['Parent']] = relationship('Parent', back_populates='bautismos_como_padre', foreign_keys=[idPadre])
    madre_record: Mapped[Optional['Parent']] = relationship('Parent', back_populates='bautismos_como_madre', foreign_keys=[idMadre])
    padrino_del_bautismo: Mapped[Optional['Padrino']] = relationship('Padrino', back_populates='bautismos_apadrinados', foreign_keys=[idPadrino])


class DataSheet(Base):
    __tablename__ = 'DataSheet'
    __table_args__ = (
        ForeignKeyConstraint(['idCatequizado'], ['Persons.Catequizado.idPerson'], name='DataSheetCatequizado_FK'),
        ForeignKeyConstraint(['idInstitution'], ['Institutions.Institution.idInstitution'], name='DataSheetInstitution_FK'), # Institución relacionada a la ficha
        ForeignKeyConstraint(['idMama'], ['Persons.Parent.idPerson'], name='DataSheetMadre_FK'),
        ForeignKeyConstraint(['idPapa'], ['Persons.Parent.idPerson'], name='DataSheetPadre_FK'),
        PrimaryKeyConstraint('idDataSheet', name='DataSheet_PK'),
        {'schema': 'Documents'}
    )
    idDataSheet: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True)
    schoolsName: Mapped[str] = mapped_column(Unicode(100)) # Ajustada longitud
    schoolGrade: Mapped[str] = mapped_column(Unicode(30)) # Cambiado a Unicode
    idCatequizado: Mapped[Optional[int]] = mapped_column(Integer) # FK
    sonNumbr: Mapped[Optional[int]] = mapped_column(Integer) # Corregido nombre
    numbrBrothers: Mapped[Optional[int]] = mapped_column(Integer) # Corregido nombre
    livesWith: Mapped[Optional[str]] = mapped_column(Unicode(50))
    residentialPhone: Mapped[Optional[str]] = mapped_column(Unicode(15))
    mainAddress: Mapped[Optional[str]] = mapped_column(Unicode(150))
    idPapa: Mapped[Optional[int]] = mapped_column(Integer) # FK a Parent
    idMama: Mapped[Optional[int]] = mapped_column(Integer) # FK a Parent
    idInstitution: Mapped[Optional[int]] = mapped_column(Integer) # FK a Institution (ej. parroquia que la recibe)
    idCertificate: Mapped[Optional[int]] = mapped_column(Integer) # FK a LevelCertificate? (Necesita definir tabla)
    idLevel: Mapped[Optional[int]] = mapped_column(Integer) # FK a Level? (Necesita definir tabla)

    catequizado_en_ficha: Mapped[Optional['Catequizado']] = relationship('Catequizado', back_populates='fichas_datos', foreign_keys=[idCatequizado])
    institucion_ficha: Mapped[Optional['Institution']] = relationship('Institution', back_populates='fichas_datos_institucion', foreign_keys=[idInstitution])
    papa_record: Mapped[Optional['Parent']] = relationship('Parent', back_populates='datasheets_como_papa', foreign_keys=[idPapa])
    mama_record: Mapped[Optional['Parent']] = relationship('Parent', back_populates='datasheets_como_mama', foreign_keys=[idMama])


class ParrocoAuth(Document): # Asumiendo que ParrocoAuth ES un Document
    __tablename__ = 'ParrocoAuth'
    __table_args__ = (
        ForeignKeyConstraint(['idDocument'], ['Documents.Document.idDocument'], name='ParrocoAuthDocument_FK'),
        ForeignKeyConstraint(['idCatequizado'], ['Persons.Catequizado.idPerson'], name='ParrocoAuthCatequizado_FK'),
        ForeignKeyConstraint(['idParroquia'], ['Institutions.Parroquia.idInstitution'], name='ParrocoAuthParroquia_FK'),
        PrimaryKeyConstraint('idDocument', name='ParrocoAuth_PK'),
        {'schema': 'Documents'}
    )
    idDocument: Mapped[int] = mapped_column(Integer, ForeignKey('Documents.Document.idDocument'), primary_key=True)
    # type: Mapped[str] = mapped_column(Unicode(50)) # 'type' ya está en Document. Aquí sería un tipo específico de autorización
    auth_type_specific: Mapped[str] = mapped_column('type', Unicode(50)) # Renombrar para evitar colisión si 'type' es de Document
    dueDate: Mapped[datetime.date] = mapped_column(Date)
    idParroquia: Mapped[int] = mapped_column(Integer) # FK a Parroquia
    idCatequizado: Mapped[int] = mapped_column(Integer) # FK a Catequizado
    description: Mapped[Optional[str]] = mapped_column(Text)

    document_base: Mapped['Document'] = relationship('Document', back_populates='parroco_auth_detail', foreign_keys=[idDocument])
    catequizado_autorizado: Mapped['Catequizado'] = relationship('Catequizado', back_populates='autorizaciones_parroco', foreign_keys=[idCatequizado])
    parroquia_que_autoriza: Mapped['Parroquia'] = relationship('Parroquia', back_populates='autorizaciones_emitidas', foreign_keys=[idParroquia])

    __mapper_args__ = {
        'polymorphic_identity': 'parroco_auth', # Si Document tiene polimorfismo
        'inherit_condition': idDocument == Document.idDocument
    }


class Payment(Base):
    __tablename__ = 'Payment'
    __table_args__ = (
        ForeignKeyConstraint(['idCatequizado'], ['Persons.Catequizado.idPerson'], name='PaymentCatequizado_FK'),
        PrimaryKeyConstraint('idPayment', name='Payment_PK'),
        {'schema': 'Documents'}
    )
    idPayment: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True)
    amount: Mapped[decimal.Decimal] = mapped_column(DECIMAL(10, 2))
    paymentMethod: Mapped[str] = mapped_column(Unicode(30))
    paymentState: Mapped[bool] = mapped_column(Boolean)
    paymentDate: Mapped[datetime.date] = mapped_column(Date)
    idCatequizado: Mapped[int] = mapped_column(Integer) # FK a Catequizado

    catequizado_del_pago: Mapped['Catequizado'] = relationship('Catequizado', back_populates='pagos_realizados', foreign_keys=[idCatequizado])

# --- Esquema Nivel ---

class Level(Base): # Tabla de definición de niveles
    __tablename__ = 'Level'
    __table_args__ = (
        ForeignKeyConstraint(['idNextLevel'], ['Nivel.Level.idLevel'], name='NextLevel_FK'),
        ForeignKeyConstraint(['idEnabledSacrament'], ['Sacraments.Sacrament.idSacrament'], name='LevelSacramento_FK'), # Sacramento que habilita este nivel
        PrimaryKeyConstraint('idLevel', name='Level_PK'),
        {'schema': 'Nivel'}
    )
    idLevel: Mapped[int] = mapped_column(Integer, primary_key=True) # Asumo que no es IDENTITY si son niveles fijos
    name: Mapped[str] = mapped_column(Unicode(30))
    description: Mapped[str] = mapped_column(Text)
    idNextLevel: Mapped[Optional[int]] = mapped_column(Integer) # FK a sí mismo
    numberOfOrder: Mapped[Optional[int]] = mapped_column(Integer)
    idEnabledSacrament: Mapped[Optional[int]] = mapped_column(Integer) # FK a Sacrament

    # Relación recursiva para el siguiente nivel
    siguiente_nivel: Mapped[Optional['Level']] = relationship('Level', remote_side=[idLevel], foreign_keys=[idNextLevel], back_populates='niveles_previos')
    niveles_previos: Mapped[List['Level']] = relationship('Level', remote_side=[idNextLevel], foreign_keys=[idNextLevel], back_populates='siguiente_nivel') # Check this logic

    # Sacramento que este nivel habilita
    sacramento_habilitado: Mapped[Optional['Sacrament']] = relationship('Sacrament', back_populates='niveles_que_lo_habilitan', foreign_keys=[idEnabledSacrament])
    
    # Cursos que son de este tipo de Nivel
    cursos_de_este_nivel: Mapped[List['Curso']] = relationship('Curso', back_populates='tipo_nivel', foreign_keys='Curso.idLevel')


class Curso(Base): # Instancia de un nivel que se imparte
    __tablename__ = 'Curso'
    __table_args__ = (
        ForeignKeyConstraint(['idLevel'], ['Nivel.Level.idLevel'], name='CursoLevel_FK'),
        ForeignKeyConstraint(['idParroquia'], ['Institutions.Institution.idInstitution'], name='CursoParroquia_FK'), # Parroquia que imparte
        ForeignKeyConstraint(['idCatequista'], ['Persons.Catequista.idPerson'], name='CursoCatequista_FK'),
        ForeignKeyConstraint(['idAyudante'], ['Persons.Ayudante.idPerson'], name='CursoAyudante_FK'), # Corregido FK a Ayudante
        PrimaryKeyConstraint('idCurso', name='Curso_PK'),
        {'schema': 'Nivel'}
    )
    idCurso: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True)
    idLevel: Mapped[int] = mapped_column(Integer)           # FK a Level (tipo de nivel)
    idParroquia: Mapped[int] = mapped_column(Integer)       # FK a Institution (Parroquia)
    idCatequista: Mapped[int] = mapped_column(Integer)      # FK a Catequista (principal)
    idAyudante: Mapped[Optional[int]] = mapped_column(Integer)  # FK a Ayudante (opcional)
    periodYear: Mapped[int] = mapped_column(Integer)
    startDate: Mapped[datetime.date] = mapped_column(Date)
    duration: Mapped[int] = mapped_column(Integer) # En semanas? días?
    endDate: Mapped[Optional[datetime.date]] = mapped_column(Date)

    tipo_nivel: Mapped['Level'] = relationship('Level', back_populates='cursos_de_este_nivel', foreign_keys=[idLevel])
    parroquia_del_curso: Mapped['Institution'] = relationship('Institution', back_populates='cursos_impartidos_aqui', foreign_keys=[idParroquia])
    catequista_principal: Mapped['Catequista'] = relationship('Catequista', back_populates='cursos_asignados', foreign_keys=[idCatequista])
    ayudante_asignado: Mapped[Optional['Ayudante']] = relationship('Ayudante', back_populates='cursos_como_ayudante', foreign_keys=[idAyudante])

    # Relaciones con documentos/eventos del curso
    asistencias_curso: Mapped[List['Attendance']] = relationship('Attendance', back_populates='curso_asistencia', foreign_keys='Attendance.idCurso')
    aprobaciones_curso: Mapped[List['LevelAprobation']] = relationship('LevelAprobation', back_populates='curso_aprobacion', foreign_keys='LevelAprobation.idCurso')
    certificados_curso: Mapped[List['LevelCertificate']] = relationship('LevelCertificate', back_populates='curso_certificado', foreign_keys='LevelCertificate.idCurso')

    # Relación Muchos a Muchos con Catequizado a través de la tabla Grupos
    catequizados_inscritos: Mapped[List['Catequizado']] = relationship(
        'Catequizado',
        secondary='Nivel.Grupos', # Nombre de la tabla de asociación con esquema
        back_populates='cursos_inscrito'
    )

# Tabla de asociación para la relación Muchos a Muchos entre Catequizado y Curso
t_Grupos = Table(
    'Grupos', Base.metadata,
    Column('idCatequizado', Integer, ForeignKey('Persons.Catequizado.idPerson'), primary_key=True),
    Column('idCurso', Integer, ForeignKey('Nivel.Curso.idCurso'), primary_key=True),
    schema='Nivel'
)


# --- Documentos relacionados a Cursos/Niveles (independientes) ---

class Attendance(Base):
    __tablename__ = 'Attendance'
    __table_args__ = (
        ForeignKeyConstraint(['idCurso'], ['Nivel.Curso.idCurso'], name='AttendanceCurso_FK'),
        ForeignKeyConstraint(['idCatequizado'], ['Persons.Catequizado.idPerson'], name='AttendanceCatequizado_FK'),
        ForeignKeyConstraint(['idCatequista'], ['Persons.Catequista.idPerson'], name='AttendanceCatequista_FK'), # Catequista que tomó asistencia
        PrimaryKeyConstraint('idCurso', 'idCatequizado', 'dateOfAttendance', name='Attendance_PK'), # PK Compuesta
        {'schema': 'Documents'} # O 'Nivel' si es más apropiado
    )
    idCurso: Mapped[int] = mapped_column(Integer, primary_key=True)
    idCatequizado: Mapped[int] = mapped_column(Integer, primary_key=True)
    dateOfAttendance: Mapped[datetime.date] = mapped_column(Date, primary_key=True)
    state: Mapped[bool] = mapped_column(Boolean) # True = presente, False = ausente
    idCatequista: Mapped[int] = mapped_column(Integer) # FK

    curso_asistencia: Mapped['Curso'] = relationship('Curso', back_populates='asistencias_curso', foreign_keys=[idCurso])
    catequizado_asistente: Mapped['Catequizado'] = relationship('Catequizado', back_populates='asistencias', foreign_keys=[idCatequizado])
    catequista_que_registra: Mapped['Catequista'] = relationship('Catequista', back_populates='asistencias_tomadas', foreign_keys=[idCatequista])


class LevelAprobation(Base):
    __tablename__ = 'LevelAprobation'
    __table_args__ = (
        ForeignKeyConstraint(['idCurso'], ['Nivel.Curso.idCurso'], name='LevelAprobationCurso_FK'),
        ForeignKeyConstraint(['idCatequizado'], ['Persons.Catequizado.idPerson'], name='LevelAprobationCatequizado_FK'),
        ForeignKeyConstraint(['idCatequista'], ['Persons.Catequista.idPerson'], name='LevelAprobationCatequista_FK'), # Catequista que aprueba
        PrimaryKeyConstraint('idLevelAprobation', name='LevelAprobation_PK'),
        {'schema': 'Documents'}
    )
    idLevelAprobation: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True)
    resultOfLevel: Mapped[bool] = mapped_column(Boolean)
    commentaries: Mapped[str] = mapped_column(Text)
    idCurso: Mapped[int] = mapped_column(Integer) # FK
    idCatequizado: Mapped[int] = mapped_column(Integer) # FK
    idCatequista: Mapped[int] = mapped_column(Integer) # FK

    curso_aprobacion: Mapped['Curso'] = relationship('Curso', back_populates='aprobaciones_curso', foreign_keys=[idCurso])
    catequizado_aprobado: Mapped['Catequizado'] = relationship('Catequizado', back_populates='aprobaciones_nivel', foreign_keys=[idCatequizado])
    catequista_que_aprueba: Mapped['Catequista'] = relationship('Catequista', back_populates='aprobaciones_emitidas', foreign_keys=[idCatequista])


class LevelCertificate(Base):
    __tablename__ = 'LevelCertificate'
    __table_args__ = (
        ForeignKeyConstraint(['idCurso'], ['Nivel.Curso.idCurso'], name='LevelCertificateCurso_FK'),
        ForeignKeyConstraint(['idCatequizado'], ['Persons.Catequizado.idPerson'], name='LevelCertificateCatequizado_FK'),
        ForeignKeyConstraint(['idCatequista'], ['Persons.Catequista.idPerson'], name='LevelCertificateCatequista_FK'), # Catequista en el certificado
        ForeignKeyConstraint(['idEclesiastico'], ['Persons.Eclesiastico.idPerson'], name='LevelCertificateEclesiastico_FK'), # Eclesiastico que firma
        PrimaryKeyConstraint('idLevelCertificate', name='LevelCertificate_PK'),
        {'schema': 'Documents'}
    )
    idLevelCertificate: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True)
    commentaries: Mapped[str] = mapped_column(Text)
    idCurso: Mapped[int] = mapped_column(Integer) # FK
    idCatequizado: Mapped[int] = mapped_column(Integer) # FK
    idCatequista: Mapped[int] = mapped_column(Integer) # FK
    idEclesiastico: Mapped[int] = mapped_column(Integer) # FK
    deliveryDate: Mapped[datetime.date] = mapped_column(Date)
    catequesisPrhase: Mapped[Optional[str]] = mapped_column(Unicode(200)) # frase en tu BD
    parroquiaLogo: Mapped[Optional[str]] = mapped_column(Unicode(300)) # logo en tu BD

    curso_certificado: Mapped['Curso'] = relationship('Curso', back_populates='certificados_curso', foreign_keys=[idCurso])
    catequizado_certificado: Mapped['Catequizado'] = relationship('Catequizado', back_populates='certificados_nivel', foreign_keys=[idCatequizado])
    catequista_que_certifica: Mapped['Catequista'] = relationship('Catequista', back_populates='certificados_emitidos', foreign_keys=[idCatequista])
    eclesiastico_que_firma: Mapped['Eclesiastico'] = relationship('Eclesiastico', back_populates='certificados_firmados', foreign_keys=[idEclesiastico])


# --- Esquema Sacraments ---

class Sacrament(Base): # Definición de tipos de sacramentos o celebraciones específicas
    __tablename__ = 'Sacrament'
    __table_args__ = (
        ForeignKeyConstraint(['idInstitution'], ['Institutions.Parroquia.idInstitution'], name='SacramentParroquia_FK'), # Parroquia donde se celebra
        PrimaryKeyConstraint('idSacrament', name='Sacrament_PK'),
        Index('Sacramenttype_IDX', 'type'),
        {'schema': 'Sacraments'}
    )
    idSacrament: Mapped[int] = mapped_column(Integer, primary_key=True) # Podría ser IDENTITY si son celebraciones, o fijo si son tipos
    celebrationDate: Mapped[datetime.date] = mapped_column(Date) # Si es una celebración específica
    observations: Mapped[str] = mapped_column(Text)
    type: Mapped[str] = mapped_column(Unicode(30)) # Ej: 'Confirmacion', 'Eucaristia', 'Reconciliacion'
    idInstitution: Mapped[int] = mapped_column(Integer) # FK a Parroquia

    parroquia_celebracion: Mapped['Parroquia'] = relationship('Parroquia', back_populates='sacramentos_celebrados_aqui', foreign_keys=[idInstitution])
    
    # Niveles que habilitan este sacramento
    niveles_que_lo_habilitan: Mapped[List['Level']] = relationship('Level', back_populates='sacramento_habilitado', foreign_keys='Level.idEnabledSacrament')
    
    # Catequizados que han recibido este sacramento (a través de CatequizadoSacramento)
    catequizados_que_recibieron: Mapped[List['CatequizadoSacramento']] = relationship('CatequizadoSacramento', back_populates='sacramento_recibido', foreign_keys='CatequizadoSacramento.idSacramento')


class CatequizadoSacramento(Base): # Tabla de unión: qué catequizado recibió qué sacramento (y con qué padrino)
    __tablename__ = 'CatequizadoSacramento'
    __table_args__ = (
        ForeignKeyConstraint(['idSacramento'], ['Sacraments.Sacrament.idSacrament'], name='SacramentSacrament_FK'),
        ForeignKeyConstraint(['idCatequizado'], ['Persons.Catequizado.idPerson'], name='SacramentCatequizado_FK'),
        ForeignKeyConstraint(['idPadrino'], ['Persons.Padrino.idPerson'], name='CatequizadoSacramentoPadrino_FK'),
        PrimaryKeyConstraint('idSacramento', 'idCatequizado', name='CatequizadoSacramento_PK'),
        {'schema': 'Sacraments'}
    )
    idSacramento: Mapped[int] = mapped_column(Integer, primary_key=True)
    idCatequizado: Mapped[int] = mapped_column(Integer, primary_key=True)
    idPadrino: Mapped[Optional[int]] = mapped_column(Integer) # FK a Padrino

    sacramento_recibido: Mapped['Sacrament'] = relationship('Sacrament', back_populates='catequizados_que_recibieron', foreign_keys=[idSacramento])
    catequizado_que_recibe: Mapped['Catequizado'] = relationship('Catequizado', back_populates='sacramentos_recibidos', foreign_keys=[idCatequizado])
    padrino_del_sacramento: Mapped[Optional['Padrino']] = relationship('Padrino', back_populates='sacramentos_apadrinados', foreign_keys=[idPadrino])


# --- Definiciones de Vistas (como Tablas solo para consulta) ---
# Estas no se usarán para inserciones/actualizaciones vía ORM directamente.
# Si necesitas interactuar con ellas como objetos, podrías definir clases simples sin relaciones complejas.

t_v_InfoAyudanteCatequista = Table(
    'v_InfoAyudanteCatequista', Base.metadata,
    Column('ID', Integer),
    Column('PrimerNombre', Unicode(30)),
    Column('SegundoNombre', Unicode(30)),
    Column('PrimerApellido', Unicode(30)),
    Column('SegundoApellido', Unicode(30)),
    Column('Sexo', CHAR(1)),
    # Column('Curso', Integer), # Faltaba en tu definición original de la vista pero estaba en el SP
    Column('Desde', Date),
    schema='Persons',
    info={'is_view': True} # Para marcarla como vista
)

# ... (definiciones similares para las otras vistas, solo con Column())

# Nota sobre las vistas:
# Para consultar vistas, usualmente se usa text() o se pueden crear modelos muy simples si es necesario.
# Ejemplo de modelo simple para una vista (si se quiere tratar como objeto):
# class InfoCatequistaView(Base):
# __table__ = t_v_InfoCatequista
# __mapper_args__ = {'primary_key': [t_v_InfoCatequista.c.ID]} # Necesita una PK para el ORM