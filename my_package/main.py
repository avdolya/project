import uvicorn
from fastapi import FastAPI
from .core.database import db_helper
from .core.models.base import Base
from .api_v1.demo_jwt_auth import router as demo_jwt_auth_router
from .api_v1.endpoints import (
    places,
    users,
    reviews,
    visited_places
)

app = FastAPI()

app.include_router(users.router)
app.include_router(places.router)
app.include_router(reviews.router)
app.include_router(visited_places.router)
app.include_router(demo_jwt_auth_router)

@app.on_event("startup")
async def startup():
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == '__main__':
    uvicorn.run(app)


