from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from sqlmodel import Session
from .db import engine, create_db_and_tables
from .middleware import register_request_logging_middleware
from .routes import main_router
from .services import set_services


def configure_server_logging() -> None:
    # Hide default request/access and startup info logs from Uvicorn.
    logging.getLogger('uvicorn.access').disabled = True
    logging.getLogger('uvicorn.access').propagate = False
    logging.getLogger('uvicorn.error').setLevel(logging.ERROR)

    # Keep SQLAlchemy quiet unless there is an error.
    logging.getLogger('sqlalchemy').setLevel(logging.ERROR)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)
    logging.getLogger('sqlalchemy.pool').setLevel(logging.ERROR)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_db_and_tables()
    session = Session(engine)
    set_services(session=session)

    yield
    
    # Shutdown
    session.close()


configure_server_logging()
app = FastAPI(lifespan=lifespan)
register_request_logging_middleware(app)


app.include_router(main_router, prefix='/api/v1')