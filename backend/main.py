import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from neo4j.exceptions import Neo4jError

# Load environment
load_dotenv()

from db import get_driver, close_driver, run_query
from routers import (
    patients,
    doctors,
    appointments,
    consultations,
    labtests,
    bills,
    dashboard,
    queries
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Driver initialization
    try:
        get_driver()
        print("Neo4j Driver initialized successfully.")
    except Exception as e:
        print(f"Warning: Could not initialize Neo4j driver at startup: {e}")
    yield
    # Close driver on shutdown
    close_driver()
    print("Neo4j Driver closed.")


app = FastAPI(
    title="CityCare Hospital Management System API",
    description="Backend REST API powered by FastAPI and Neo4j Graph Database",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Setup
frontend_origins_raw = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
origins = [o.strip() for o in frontend_origins_raw.split(",") if o.strip()]
default_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://localhost:3000",
]
for orig in default_origins:
    if orig not in origins:
        origins.append(orig)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global database error handler
@app.exception_handler(Neo4jError)
async def neo4j_exception_handler(request: Request, exc: Neo4jError):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Neo4j Database Error: {exc.message}"}
    )


# Health Check Endpoint
@app.get("/api/health", tags=["Health"])
def health_check():
    """Runs RETURN 1 to check database connectivity."""
    try:
        result = run_query("RETURN 1 AS status")
        return {"status": "ok", "database": "connected", "result": result[0]["status"]}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "database": "disconnected", "detail": str(e)}
        )


# Insurance companies (used by the Billing page dropdown)
@app.get("/api/insurance-companies", tags=["Billing & Invoices"])
def list_insurance_companies():
    try:
        rows = run_query("""
            MATCH (n)
            WHERE n.companyId IS NOT NULL AND n.companyId <> ''
            RETURN DISTINCT n.companyId AS name
            ORDER BY name
        """)
        return [{"companyId": r["name"], "name": r["name"]} for r in rows]
    except Exception as e:
        print(f"insurance-companies error: {e}")
        return []


# Register Routers under /api
api_prefix = "/api"
app.include_router(patients.router, prefix=api_prefix)
app.include_router(doctors.router, prefix=api_prefix)
app.include_router(appointments.router, prefix=api_prefix)
app.include_router(consultations.router, prefix=api_prefix)
app.include_router(labtests.router, prefix=api_prefix)
app.include_router(bills.router, prefix=api_prefix)
app.include_router(dashboard.router, prefix=api_prefix)
app.include_router(queries.router, prefix=api_prefix)


@app.get("/", include_in_schema=False)
def root():
    return {"message": "CityCare Hospital Management API is running. Visit /docs for Swagger."}