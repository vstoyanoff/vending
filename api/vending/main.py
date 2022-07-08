from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from vending.db import setup as db_setup
from vending.routers import auth, products, users

db_setup()
app = FastAPI()

origins = ["http://localhost", "http://localhost:8000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(users.router)


@app.get("/health")
def health():
    return {"status": "ok"}
