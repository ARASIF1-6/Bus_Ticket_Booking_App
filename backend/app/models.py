from sqlalchemy import Column, Integer, String, ForeignKey, Date, DateTime, Text
from sqlalchemy.orm import relationship
from .database import Base
import datetime

class District(Base):
    __tablename__ = "districts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    dropping_points = relationship("DroppingPoint", back_populates="district")

class DroppingPoint(Base):
    __tablename__ = "dropping_points"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    price = Column(Integer)
    district_id = Column(Integer, ForeignKey("districts.id"))
    district = relationship("District", back_populates="dropping_points")

class BusProvider(Base):
    __tablename__ = "bus_providers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    coverage = Column(Text)  # JSON str or comma separated
    # optionally store path to policy file
    policy_path = Column(String, nullable=True)

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    passenger_name = Column(String)
    phone = Column(String)
    from_district = Column(String)
    to_district = Column(String)
    dropping_point = Column(String)
    fare = Column(Integer)
    travel_date = Column(String)  # ISO date string (YYYY-MM-DD)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default="CONFIRMED")  # CONFIRMED or CANCELED
