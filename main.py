from contextlib import asynccontextmanager

from fastapi import FastAPI
from windrop.router import router as windrop_router

import migrate
from database.database import database


@asynccontextmanager
async def lifespan(app: FastAPI):
    migrate.migrate_database()
    try:
        yield
    finally:
        database.close()


app = FastAPI(lifespan=lifespan)
app.include_router(router=windrop_router)
