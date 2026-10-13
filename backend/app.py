"""Application entry‑point – creates the FastAPI instance and includes the
router defined in ``backend.routes``.  The file is deliberately tiny so that
running ``uvicorn backend.app:app`` starts the service.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes import router

app = FastAPI(
    title="TCC – Algoritmo Genético – API",
    version="0.1.0",
    description="FastAPI wrapper exposing the scientific core of the TCC‑AG "
    "prototype.  Endpoints return the same structures used by the original "
    "Streamlit demo, enabling a clean React frontend later.",
)

# The React dev server (Vite default port 5173) and local builds may live on a
# different origin during development; permit it explicitly rather than "*".
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
