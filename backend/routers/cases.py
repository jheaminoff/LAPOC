"""Cases router — look up a specific case by ID."""

import random

from database import get_db
from fastapi import APIRouter, Depends, HTTPException
from models import Case
from schemas import CaseOut
from sqlalchemy.orm import Session

router = APIRouter(prefix="/cases", tags=["cases"])


@router.get("/random")
def random_case(db: Session = Depends(get_db)):
    """Return a random case ID from the database."""
    case_ids = db.query(Case.case_id).all()
    if not case_ids:
        raise HTTPException(status_code=404, detail="No cases found")
    case = random.choice(case_ids)
    return {"case_id": case.case_id}


@router.get("/{case_id}", response_model=CaseOut)
def get_case(case_id: str, db: Session = Depends(get_db)):
    """Return full details for a single case."""
    case = db.query(Case).filter(Case.case_id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
    return case
