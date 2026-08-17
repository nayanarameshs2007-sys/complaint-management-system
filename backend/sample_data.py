"""
Seed database with realistic sample complaints for demo
"""
from database import SessionLocal, engine
from models import Base, Complaint
import datetime

INITIAL_SAMPLES = [
    {
        "complaint_id": "CMP-1001",
        "description": "Large pothole near central bus stand causing severe traffic slowdown and rim damage.",
        "location": "Central Bus Stand",
        "category": "Road Damage",
        "priority": "HIGH",
        "department": "Public Works",
        "status": "In Progress",
        "duplicate_of": None,
        "similarity_score": None
    },
    {
        "complaint_id": "CMP-1002",
        "description": "Huge pothole at central bus stand dangerous for two-wheelers.",
        "location": "Central Bus Stand",
        "category": "Road Damage",
        "priority": "HIGH",
        "department": "Public Works",
        "status": "Submitted",
        "duplicate_of": "CMP-1001",
        "similarity_score": 85
    },
    {
        "complaint_id": "CMP-1003",
        "description": "Dangerous deep pothole near central bus stand entrance.",
        "location": "Central Bus Stand Entrance",
        "category": "Road Damage",
        "priority": "HIGH",
        "department": "Public Works",
        "status": "Submitted",
        "duplicate_of": "CMP-1001",
        "similarity_score": 78
    },
    {
        "complaint_id": "CMP-1004",
        "description": "Fallen live electric wire sparking near St. Jude school main gate!",
        "location": "St. Jude School Gate, Ward 5",
        "category": "Electrical Hazard",
        "priority": "CRITICAL",
        "department": "Electrical Department",
        "status": "In Progress",
        "duplicate_of": None,
        "similarity_score": None
    },
    {
        "complaint_id": "CMP-1005",
        "description": "Garbage heap left uncollected near vegetable market for 4 days.",
        "location": "Main Market Area",
        "category": "Waste Management",
        "priority": "MEDIUM",
        "department": "Sanitation",
        "status": "Submitted",
        "duplicate_of": None,
        "similarity_score": None
    },
    {
        "complaint_id": "CMP-1006",
        "description": "Streetlight not functioning in Sector 7 lane 3, complete darkness at night.",
        "location": "Sector 7, Lane 3",
        "category": "Street Lighting",
        "priority": "MEDIUM",
        "department": "Electrical Department",
        "status": "Submitted",
        "duplicate_of": None,
        "similarity_score": None
    },
    {
        "complaint_id": "CMP-1007",
        "description": "Major underground water pipeline leakage flooding the main road.",
        "location": "MG Road Crossing",
        "category": "Water Supply & Sewage",
        "priority": "CRITICAL",
        "department": "Water Authority",
        "status": "In Progress",
        "duplicate_of": None,
        "similarity_score": None
    },
    {
        "complaint_id": "CMP-1008",
        "description": "Open sewage drain overflowing near residential apartments.",
        "location": "Sunrise Heights, Block B",
        "category": "Water Supply & Sewage",
        "priority": "HIGH",
        "department": "Sanitation",
        "status": "Submitted",
        "duplicate_of": None,
        "similarity_score": None
    },
    {
        "complaint_id": "CMP-1009",
        "description": "Broken road divider tiles scattered on highway causing risk.",
        "location": "City Highway Flyover",
        "category": "Road Damage",
        "priority": "MEDIUM",
        "department": "Public Works",
        "status": "Resolved",
        "duplicate_of": None,
        "similarity_score": None
    },
    {
        "complaint_id": "CMP-1010",
        "description": "Fallen tree branch blocking traffic lane near hospital entrance.",
        "location": "City General Hospital Gate",
        "category": "Public Safety / Obstruction",
        "priority": "HIGH",
        "department": "Traffic & Safety",
        "status": "Resolved",
        "duplicate_of": None,
        "similarity_score": None
    },
    {
        "complaint_id": "CMP-1011",
        "description": "No drinking water supply in Ward 12 for past 24 hours.",
        "location": "Ward 12 Residential Zone",
        "category": "Water Supply & Sewage",
        "priority": "HIGH",
        "department": "Water Authority",
        "status": "Submitted",
        "duplicate_of": None,
        "similarity_score": None
    },
    {
        "complaint_id": "CMP-1012",
        "description": "Broken streetlight pole leaning dangerously towards pavement.",
        "location": "Railway Station Road",
        "category": "Electrical Hazard",
        "priority": "CRITICAL",
        "department": "Electrical Department",
        "status": "Submitted",
        "duplicate_of": None,
        "similarity_score": None
    }
]

def seed_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # Check if data already exists
    if db.query(Complaint).count() == 0:
        for data in INITIAL_SAMPLES:
            complaint = Complaint(**data)
            db.add(complaint)
        db.commit()
        print("Database successfully seeded with initial sample complaints!")
    else:
        print("Database already contains records. Skipping seed.")
    db.close()

if __name__ == "__main__":
    seed_db()
