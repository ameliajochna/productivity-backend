import os

import sqlalchemy
import sqlalchemy.ext.declarative
import sqlalchemy.orm

user = os.environ['GCP_DB_USER']
password = os.environ['GCP_DB_PASSWORD']
host = os.environ['GCP_DB_HOST']
port = os.environ['GCP_DB_PORT']
name = os.environ['GCP_DB_NAME']


DATABASE_URL = f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}'

engine = sqlalchemy.create_engine(DATABASE_URL)

SessionLocal = sqlalchemy.orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = sqlalchemy.orm.declarative_base()
