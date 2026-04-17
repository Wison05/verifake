from fastapi import FastAPI
from services.backend.routers import media

app = FastAPI()

app.include_router(media.router, prefix="/media")