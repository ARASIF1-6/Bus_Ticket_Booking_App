import os, json
from .database import SessionLocal, engine
from . import models
from sqlalchemy.orm import Session

DATA_JSON = os.getenv("DATA_JSON_PATH", "/data/data.json")
SHYAMOLI_PATH = os.getenv("SHYAMOLI_PATH", "/data/shyamoli.txt")
SOUDIA_PATH = os.getenv("SOUDIA_PATH", "/data/soudia.txt")

def load_data_once():
    # Create tables
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # if districts already exist, skip
        if db.query(models.District).first():
            return
        with open(DATA_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
        # districts
        for d in data.get("districts", []):
            district = models.District(name=d["name"])
            db.add(district)
            db.commit()
            db.refresh(district)
            for dp in d.get("dropping_points", []):
                dp_model = models.DroppingPoint(name=dp["name"], price=dp["price"], district_id=district.id)
                db.add(dp_model)
            db.commit()
        # providers
        for p in data.get("bus_providers", []):
            # find policy path if matches known ones:
            policy_path = None
            if p["name"].lower() == "shyamoli" and os.path.exists(SHYAMOLI_PATH):
                policy_path = SHYAMOLI_PATH
            if p["name"].lower() == "soudia" and os.path.exists(SOUDIA_PATH):
                policy_path = SOUDIA_PATH
            provider = models.BusProvider(name=p["name"], coverage=json.dumps(p.get("coverage_districts", [])), policy_path=policy_path)
            db.add(provider)
        db.commit()
    finally:
        db.close()
