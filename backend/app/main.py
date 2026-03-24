from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from . import database, crud, schemas, data_loader, rag, models
import os

app = FastAPI(title="Bus Booking App")

templates = Jinja2Templates(directory="app/templates")

# create tables and load initial data
data_loader.load_data_once()

# dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/districts")
def list_districts(db: Session = Depends(get_db)):
    ds = crud.get_districts(db)
    return [{"name": d.name, "dropping_points": [{"name": p.name, "price": p.price} for p in d.dropping_points] } for d in ds]

@app.get("/api/search")
def search_buses(from_district: str, to_district: str, max_fare: int = None, db: Session = Depends(get_db)):
    results = crud.find_buses(db, from_district, to_district, max_fare)
    return {"results": results}

@app.post("/api/book", response_model=schemas.BookingOut)
def book_ticket(booking: schemas.BookingCreate, db: Session = Depends(get_db)):
    b = crud.create_booking(db, booking)
    return b

@app.get("/api/bookings/{booking_id}")
def get_booking(booking_id: int, db: Session = Depends(get_db)):
    b = crud.get_booking(db, booking_id)
    if not b:
        raise HTTPException(status_code=404, detail="Booking not found")
    return b

@app.get("/api/bookings")
def bookings_by_phone(phone: str, db: Session = Depends(get_db)):
    return crud.get_bookings_by_phone(db, phone)

@app.post("/api/bookings/{booking_id}/cancel")
def cancel_booking(booking_id: int, db: Session = Depends(get_db)):
    b = crud.cancel_booking(db, booking_id)
    if not b:
        raise HTTPException(status_code=404, detail="Booking not found")
    return {"status": "canceled", "booking": b.id}

@app.get("/api/provider/{name}")
def provider_info(name: str, db: Session = Depends(get_db)):
    p = crud.get_provider_by_name(db, name)
    if not p:
        raise HTTPException(status_code=404, detail="Provider not found")
    info = {"name": p.name, "coverage": p.coverage}
    # If a policy_path exists, return its mounted container path so frontend can fetch it
    if p.policy_path and os.path.exists(p.policy_path):
        info["policy_url"] = p.policy_path
    return info

@app.get("/api/provider-file")
def provider_file(path: str):
    # path expected to be a container-mounted path such as /data/shyamoli.txt
    if os.path.exists(path):
        return FileResponse(path, media_type="text/plain")
    raise HTTPException(status_code=404, detail="File not found")

@app.get("/api/rag")
def rag_query(q: str):
    docs = rag.retrieve(q)
    answer = rag.generate_answer(q, docs)
    return {"query": q, "answer": answer, "sources": [d["source"] for d in docs]}
