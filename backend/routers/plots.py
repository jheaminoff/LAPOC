"""Plots router — look up a parcel by APN or address."""

from database import get_db
from fastapi import APIRouter, Depends, HTTPException
from models import Case, Plot
from schemas import ParcelResult
from sqlalchemy.orm import Session

router = APIRouter(prefix="/plots", tags=["plots"])


@router.get("/search/address", response_model=list[ParcelResult])
def search_by_address(q: str, db: Session = Depends(get_db)):
    """Search parcels by partial address match (case-insensitive)."""
    plots = db.query(Plot).filter(Plot.address.ilike(f"%{q}%")).limit(10).all()
    results = []
    for plot in plots:
        cases = db.query(Case).filter(Case.apn == plot.apn).all()
        results.append(ParcelResult(plot=plot, cases=cases))
    return results


@router.get("/{apn}", response_model=ParcelResult)
def get_parcel(apn: str, db: Session = Depends(get_db)):
    """Return plot info and all associated cases for an APN."""
    plot = db.query(Plot).filter(Plot.apn == apn).first()
    if not plot:
        raise HTTPException(status_code=404, detail=f"No parcel found for APN {apn}")
    cases = db.query(Case).filter(Case.apn == apn).all()
    return ParcelResult(plot=plot, cases=cases)
