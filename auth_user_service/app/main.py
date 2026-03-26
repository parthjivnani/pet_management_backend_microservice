from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.database import get_database
from routes.route import router as api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_database()
    yield
    # Optional: close motor client if needed
    # get_database().client.close()


app = FastAPI(
    title="Auth User Service",
    version="0.1.0",
    lifespan=lifespan,
)

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return "Auth user service is running!"


app.include_router(api_router, prefix="/api")
