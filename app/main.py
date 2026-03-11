from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlmodel import Session
from .db import engine, create_db_and_tables
from .routes import main_router
from .services import set_services


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_db_and_tables()
    session = Session(engine)
    set_services(session=session)

    yield
    
    # Shutdown
    session.close()


app = FastAPI(lifespan=lifespan)

app.include_router(main_router, prefix='/api/v1')