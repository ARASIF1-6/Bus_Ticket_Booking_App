from sqlalchemy.orm import Session
from . import models
import json

def get_districts(db: Session):
    return db.query(models.District).all()

def find_buses(db: Session, from_district: str, to_district: str, max_fare: int = None):
    # Simple logic:
    # find providers that cover both districts and gather dropping_points/fare for the "from" district.
    providers = db.query(models.BusProvider).all()
    results = []
    for p in providers:
        coverage = json.loads(p.coverage)
        if from_district in coverage and to_district in coverage:
            # get dropping points for from_district
            dp_query = db.query(models.DroppingPoint).join(models.District).filter(models.District.name==from_district).all()
            for dp in dp_query:
                if max_fare is None or dp.price <= max_fare:
                    results.append({
                        "provider": p.name,
                        "from": from_district,
                        "dropping_point": dp.name,
                        "fare": dp.price,
                        "to": to_district
                    })
    return results

def create_booking(db: Session, booking_data):
    booking = models.Booking(**booking_data.dict())
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking

def get_booking(db: Session, booking_id: int):
    return db.query(models.Booking).filter(models.Booking.id==booking_id).first()

def get_bookings_by_phone(db: Session, phone: str):
    return db.query(models.Booking).filter(models.Booking.phone==phone).all()

def cancel_booking(db: Session, booking_id: int):
    b = get_booking(db, booking_id)
    if not b:
        return None
    b.status = "CANCELED"
    db.commit()
    db.refresh(b)
    return b

def get_provider_by_name(db: Session, name: str):
    return db.query(models.BusProvider).filter(models.BusProvider.name.ilike(f"%{name}%")).first()
