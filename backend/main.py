"""FastAPI application entry point."""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from database import engine, Base
from routers import plots, cases, chat

load_dotenv()

# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LAPOC — LA City Planning One-Stop-Shop",
    description="Agentic chatbot for LA City planning and permit information",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(plots.router)
app.include_router(cases.router)
app.include_router(chat.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "lapoc-backend"}
