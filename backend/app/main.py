import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.db.database import init_db, get_db_connection
from backend.app.db.seed_data import seed_database
from backend.app.api.routes_monitor import router as monitor_router
from backend.app.api.routes_incidents import router as incidents_router
from backend.app.api.routes_trace import router as trace_router

app = FastAPI(
    title="PahiroWatch API",
    description="Autonomous Landslide-Risk Monitoring & Operational Response Agent for Nepal",
    version="1.0.0"
)

# Enable CORS for local React/Vite development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(monitor_router)
app.include_router(incidents_router)
app.include_router(trace_router)

@app.on_event("startup")
def on_startup():
    init_db()
    # Check if locations are seeded
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM locations")
    count = cursor.fetchone()["count"]
    conn.close()
    if count == 0:
        seed_database()

@app.get("/")
def root():
    return {
        "product": "PahiroWatch",
        "tagline": "Detect the slope. Protect the road. Alert before the disaster.",
        "status": "OPERATIONAL",
        "pilot_corridor": "Narayanghat–Mugling Highway (NH05)",
        "operator": "Ramesh, Municipal Disaster Management Officer",
        "version": "1.0.0"
    }
