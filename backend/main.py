import os
import sys
from typing import Optional

# Ensure backend directory is in sys.path for direct module resolution
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import engine, get_db, Base
from models import Complaint
from analysis import analyze_complaint
from duplicate_detection import find_possible_duplicate
from sample_data import seed_db

# Create DB tables and seed initial data
Base.metadata.create_all(bind=engine)
seed_db()

app = FastAPI(
    title="CivicPulse - Citizen Complaint Management API",
    description="Backend API for citizen complaint submission, AI analysis, routing, duplicate detection, and officer tracking."
)

# Enable CORS for local HTML frontend testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request / Response Schemas
class ComplaintCreate(BaseModel):
    description: str
    location: str
    image_path: Optional[str] = None

class StatusUpdate(BaseModel):
    status: str

class ComplaintResponse(BaseModel):
    id: int
    complaint_id: str
    description: str
    location: str
    category: str
    priority: str
    department: str
    status: str
    duplicate_of: Optional[str] = None
    similarity_score: Optional[int] = None
    created_at: str

    class Config:
        from_attributes = True

# Helper to format model to dict
def format_complaint(c: Complaint):
    return {
        "id": c.id,
        "complaint_id": c.complaint_id,
        "description": c.description,
        "location": c.location,
        "category": c.category,
        "priority": c.priority,
        "department": c.department,
        "status": c.status,
        "duplicate_of": c.duplicate_of,
        "similarity_score": c.similarity_score,
        "created_at": c.created_at.strftime("%Y-%m-%d %H:%M:%S") if c.created_at else ""
    }

# API Health Check Endpoint
@app.get("/api/health")
def api_health():
    return {"message": "CivicPulse Complaint Management API is running", "docs": "/docs"}

# 1. Submit & Analyze Complaint
@app.post("/api/complaints")
def create_complaint(payload: ComplaintCreate, db: Session = Depends(get_db)):
    if not payload.description.strip():
        raise HTTPException(status_code=400, detail="Description is required")

    # Step A: Run AI Analysis Module
    analysis = analyze_complaint(payload.description, payload.location)

    # Step B: Run Duplicate Detection against existing DB complaints
    existing = db.query(Complaint).all()
    existing_list = [{"complaint_id": item.complaint_id, "description": item.description, "location": item.location} for item in existing]
    
    dup_id, similarity = find_possible_duplicate(payload.description, payload.location, existing_list)

    # Step C: Generate unique Complaint ID (e.g. CMP-1013)
    new_id = f"CMP-{1000 + len(existing) + 1}"

    new_complaint = Complaint(
        complaint_id=new_id,
        description=payload.description,
        location=payload.location,
        image_path=payload.image_path,
        category=analysis["category"],
        priority=analysis["priority"],
        department=analysis["department"],
        status="Submitted",
        duplicate_of=dup_id,
        similarity_score=similarity if dup_id else None
    )

    db.add(new_complaint)
    db.commit()
    db.refresh(new_complaint)

    return format_complaint(new_complaint)

# 2. List Complaints with optional filtering
@app.get("/api/complaints")
def list_complaints(
    priority: Optional[str] = None,
    department: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Complaint)

    if priority:
        query = query.filter(Complaint.priority == priority.upper())
    if department:
        query = query.filter(Complaint.department.ilike(f"%{department}%"))
    if status:
        query = query.filter(Complaint.status.ilike(f"%{status}%"))

    # Return ordered by ID descending
    items = query.order_by(Complaint.id.desc()).all()
    return [format_complaint(c) for c in items]

# 3. Get Single Complaint by ID or complaint_id (e.g. CMP-1001)
@app.get("/api/complaints/{identifier}")
def get_complaint(identifier: str, db: Session = Depends(get_db)):
    if identifier.isdigit():
        c = db.query(Complaint).filter(Complaint.id == int(identifier)).first()
    else:
        c = db.query(Complaint).filter(Complaint.complaint_id.ilike(identifier.strip())).first()

    if not c:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    res = format_complaint(c)

    # Find duplicates linking to this one
    linked_duplicates = db.query(Complaint).filter(Complaint.duplicate_of == c.complaint_id).all()
    res["linked_duplicates"] = [format_complaint(d) for d in linked_duplicates]

    return res

# 4. Update Complaint Status
@app.put("/api/complaints/{identifier}/status")
def update_status(identifier: str, payload: StatusUpdate, db: Session = Depends(get_db)):
    if identifier.isdigit():
        c = db.query(Complaint).filter(Complaint.id == int(identifier)).first()
    else:
        c = db.query(Complaint).filter(Complaint.complaint_id.ilike(identifier.strip())).first()

    if not c:
        raise HTTPException(status_code=404, detail="Complaint not found")

    c.status = payload.status
    db.commit()
    db.refresh(c)
    return format_complaint(c)

# 5. Dashboard Summary Statistics
@app.get("/api/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    all_items = db.query(Complaint).all()

    total = len(all_items)
    critical = sum(1 for c in all_items if c.priority == "CRITICAL")
    high = sum(1 for c in all_items if c.priority == "HIGH")
    pending = sum(1 for c in all_items if c.status in ["Submitted", "Assigned", "In Progress"])
    resolved = sum(1 for c in all_items if c.status == "Resolved")
    duplicates = sum(1 for c in all_items if c.duplicate_of is not None)

    return {
        "total": total,
        "critical": critical,
        "high": high,
        "pending": pending,
        "resolved": resolved,
        "duplicates": duplicates
    }

from fastapi.responses import FileResponse

# Mount Frontend static files (HTML, CSS, JS)
frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

@app.get("/")
def serve_index():
    return FileResponse(os.path.join(frontend_path, "index.html"))

if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")


