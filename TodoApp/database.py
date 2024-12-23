from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base 

SQLALCHEMY_DATABASE_URL = 'sqlite:///./todosapp.db'


#if postgres
# SQLALCHEMY_DATABASE_URL = 'postgresql:///./postgres:test1234!@localhostDataBase'
# engine=create_engine(SQLALCHEMY_DATABASE_URL)


engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False})

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

Base = declarative_base()

#SQLAlchemy only creates new databases not enhance any so we use alembic