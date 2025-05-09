from sqlalchemy import create_engine, text
import pandas as pd

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

with engine.connect() as conn:
    result = conn.execute(
        text("EXEC sp_InsertPerson :id, :nombre1, :nombre2, :apellido1, :apellido2, :fecha, :sexo"),
        {
            "id": 16,
            "nombre1": "Angel",
            "nombre2": "Carlos",
            "apellido1": "Mendoza",
            "apellido2": "Salinas",
            "fecha": "2003-05-20",
            "sexo": "M"
        }
    )
    conn.commit()

query = "SELECT * FROM Institutions.v_InfoArquidiocesis"
df = pd.read_sql(query, engine)
print(df)