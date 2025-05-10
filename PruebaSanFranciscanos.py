from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from models import Catequizado
import datetime

server = 'GABO'  
database = 'SANFRANCISCANOS'

connection_string = f"mssql+pyodbc://@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server"
"&Trusted_Connection=yes&TrustedServerCertificate=yes"

engine = create_engine(connection_string)

try:
    with engine.connect() as connection:
        print("Se realizó la conexión a la base de datos")
except Exception as e:
    print(f"Ocurrió un error: {e}")


nuevo_catequizado = Catequizado(
    birthdate=datetime.date(2005, 8, 21),
    bloodType="O+",
    alergies="Polen",
    emergencyContactName="Juan Perez",
    emergencyContactPhone="0999999999",
    details="Necesita supervisión médica",
    idInstitution=3,
    state=True,

    # Datos heredados de Person
    firstName="Carlos",
    secondName="Andrés",
    lastName="Ramírez",
    secondLastName="Vera",
    sex="M"
)

# Ejecutar el procedimiento almacenado
with Session(engine) as session:
    result = session.execute(
        text("""
            DECLARE @CreatedPersonID INT;
            EXEC Persons.sp_InsertCatequizado 
                @firstName = :firstName,
                @secondName = :secondName,
                @lastName = :lastName,
                @secondLastName = :secondLastName,
                @sex = :sex,
                @birthdate = :birthdate,
                @bloodType = :bloodType,
                @alergies = :alergies,
                @emergencyContactName = :emergencyContactName,
                @emergencyContactPhone = :emergencyContactPhone,
                @details = :details,
                @idInstitution = :idInstitution,
                @state = :state,
                @CreatedPersonID = @CreatedPersonID OUTPUT;
            SELECT @CreatedPersonID AS CreatedPersonID;
        """),
        {
            "firstName": nuevo_catequizado.firstName,
            "secondName": nuevo_catequizado.secondName,
            "lastName": nuevo_catequizado.lastName,
            "secondLastName": nuevo_catequizado.secondLastName,
            "sex": nuevo_catequizado.sex,
            "birthdate": nuevo_catequizado.birthdate,
            "bloodType": nuevo_catequizado.bloodType,
            "alergies": nuevo_catequizado.alergies,
            "emergencyContactName": nuevo_catequizado.emergencyContactName,
            "emergencyContactPhone": nuevo_catequizado.emergencyContactPhone,
            "details": nuevo_catequizado.details,
            "idInstitution": nuevo_catequizado.idInstitution,
            "state": nuevo_catequizado.state,
        }
    )

    created_id = result.scalar_one()  # ID de la persona creada
    print(f"✅ Catequizado creado con ID: {created_id}")

    # (Opcional) Puedes asignarlo al objeto si lo deseas
    nuevo_catequizado.idPerson = created_id