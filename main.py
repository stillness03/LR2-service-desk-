from fastapi import FastAPI
from database import engine, Base
from routers import support_router

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Support API")

app.include_router(support_router.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # host Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)