from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

engine = None
SessionLocal = None

def init_engine(connection_string):
    global engine, SessionLocal
    engine = create_engine(connection_string)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)