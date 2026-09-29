import os
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends
from sqlmodel import Session, create_engine

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("Falta la variable de entorno DATABASE_URL")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
