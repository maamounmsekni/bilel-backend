from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, Query, Path, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import desc

from .database import get_db, engine
from .model import Base, Commande
from .schemas import CommandeCreate, CommandeUpdate, CommandeOut

app = FastAPI(title="Client Commandes API")

# CORS for Angular dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://127.0.0.1:4200",
        "https://bilel-frontend.vercel.app",  # <-- change to your real Vercel domain
    ],
     # allow preview deployments too
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
import os
@app.on_event("startup")
def on_startup():
    if os.getenv("ENV", "dev") == "dev":
        Base.metadata.create_all(bind=engine)

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/commandes", response_model=CommandeOut, status_code=status.HTTP_201_CREATED)
def create_commande(payload: CommandeCreate, db: Session = Depends(get_db)):
    row = Commande(
        client_name=payload.client_name.strip(),
        phone=payload.phone.strip(),
        address=payload.address.strip(),
        commande=payload.commande.strip(),
    )
    if payload.date is not None:
        row.date = payload.date

    db.add(row)
    db.commit()
    db.refresh(row)
    return row

# ✅ phone-only search
@app.get("/commandes", response_model=List[CommandeOut])
def list_commandes(
    db: Session = Depends(get_db),
    phone: Optional[str] = Query(None, description="Search by phone number"),
    limit: int = Query(50, ge=1, le=1000),
):
    q = db.query(Commande).order_by(desc(Commande.date), desc(Commande.id))
    if phone:
        phone = phone.strip()
        q = q.filter(Commande.phone.ilike(f"%{phone}%"))  # partial match

    return q.limit(limit).all()

@app.get("/commandes/{commande_id}", response_model=CommandeOut)
def get_commande(
    commande_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
):
    row = db.query(Commande).filter(Commande.id == commande_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Commande not found")
    return row

@app.put("/commandes/{commande_id}", response_model=CommandeOut)
def update_commande(
    payload: CommandeUpdate,
    commande_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
):
    row = db.query(Commande).filter(Commande.id == commande_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Commande not found")

    if payload.client_name is not None:
        row.client_name = payload.client_name.strip()
    if payload.phone is not None:
        row.phone = payload.phone.strip()
    if payload.address is not None:
        row.address = payload.address.strip()
    if payload.commande is not None:
        row.commande = payload.commande.strip()
    if payload.date is not None:
        row.date = payload.date

    db.commit()
    db.refresh(row)
    return row

@app.delete("/commandes/{commande_id}")
def delete_commande(
    commande_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
):
    row = db.query(Commande).filter(Commande.id == commande_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Commande not found")
    db.delete(row)
    db.commit()
    return {"ok": True}
