"""SQLAlchemy ORM models."""

from sqlalchemy import Column, Text, Integer, Float, ForeignKey, Date
from sqlalchemy.orm import relationship

from database import Base


class Plot(Base):
    __tablename__ = "plots"

    apn = Column(Text, primary_key=True, index=True)
    address = Column(Text, nullable=False)
    neighborhood = Column(Text)
    zoning = Column(Text)
    lot_size_sqft = Column(Integer)
    current_use = Column(Text)

    cases = relationship("Case", back_populates="plot")


class Case(Base):
    __tablename__ = "cases"

    case_id = Column(Text, primary_key=True, index=True)
    apn = Column(Text, ForeignKey("plots.apn"), nullable=False, index=True)
    department = Column(Text, nullable=False)       # "LADBS" | "City Planning"
    process_type = Column(Text, nullable=False)     # e.g. "Bldg-New", "CUB", "ADU"
    applicant_type = Column(Text)                   # "resident" | "developer" | "contractor"
    applicant_name = Column(Text)
    submitted_date = Column(Text)                   # ISO date string
    current_status = Column(Text)
    assigned_to = Column(Text)
    description = Column(Text)
    fees_paid = Column(Float, default=0.0)
    fees_outstanding = Column(Float, default=0.0)
    hearing_date = Column(Text)                     # ISO date string or null
    next_action = Column(Text)
    portal_url = Column(Text)
    valuation = Column(Float, nullable=True)        # Project dollar valuation (LADBS fee basis)
    pc_job_number = Column(Text, nullable=True)     # LADBS plan check job# e.g. B-24-10-00001
    plan_type = Column(Text, nullable=True)         # ADU: "standard_plan" | "custom"
    conditions_of_approval = Column(Text, nullable=True)  # JSON array of condition strings

    plot = relationship("Plot", back_populates="cases")


class WorkflowStep(Base):
    __tablename__ = "workflow_steps"

    id = Column(Integer, primary_key=True, autoincrement=True)
    process_type = Column(Text, nullable=False, index=True)
    step_order = Column(Integer, nullable=False)
    step_name = Column(Text, nullable=False)
    description = Column(Text)
    responsible_party = Column(Text)               # "Applicant" | "LADBS" | "City Planning"
    typical_days = Column(Text)                    # e.g. "3-5", "10-14"


class WorkflowPersona(Base):
    __tablename__ = "workflow_personas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    process_type = Column(Text, nullable=False, index=True)
    step_name = Column(Text, nullable=False)
    persona = Column(Text, nullable=False)          # "resident" | "developer" | "contractor"
    guidance = Column(Text)
