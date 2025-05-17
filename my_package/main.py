import uvicorn
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Request
import os
from starlette.responses import HTMLResponse
from my_package.core.database import db_helper
from my_package.core.models.base import Base
from my_package.api_v1.demo_jwt_auth import router as demo_jwt_auth_router
from my_package.api_v1.endpoints import (
    places,
    users,
    reviews,
    visited_places
)

app = FastAPI()

# настройка путей к фронтенду
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# подключение статических файлов
app.mount("/static", StaticFiles(directory=os.path.join(FRONTEND_DIR, "static")), name="static")

# подключение шаблонов
templates = Jinja2Templates(directory=os.path.join(FRONTEND_DIR, "templates"))


app.include_router(users.router)
app.include_router(places.router)
app.include_router(reviews.router)
app.include_router(visited_places.router)
app.include_router(demo_jwt_auth_router)

@app.on_event("startup")
async def startup():
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"request": request}
    )


if __name__ == '__main__':
    uvicorn.run(app)


