import os
from typing import List, Optional

from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    Path,
    Query,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import desc, or_
from sqlalchemy.orm import Session

from .database import engine, get_db
from .model import Base, Commande
from .schemas import (
    CommandeCreate,
    CommandeOut,
    CommandeUpdate,
)


app = FastAPI(title="Ilias Shop API")


# Angular frontend permissions
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://127.0.0.1:4200",
        "https://bilel-frontend.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    if os.getenv("ENV", "dev") == "dev":
        Base.metadata.create_all(bind=engine)


@app.get("/health")
def health():
    return {
        "ok": True,
        "service": "ilias-shop-api",
    }


@app.post(
    "/commandes",
    response_model=CommandeOut,
    status_code=status.HTTP_201_CREATED,
)
def create_commande(
    payload: CommandeCreate,
    db: Session = Depends(get_db),
):
    phone2 = None

    if payload.phone2:
        phone2 = payload.phone2.strip() or None

    row = Commande(
        client_name=payload.client_name.strip(),
        phone=payload.phone.strip(),
        phone2=phone2,
        address=payload.address.strip(),
        commande=payload.commande.strip(),
    )

    if payload.date is not None:
        row.date = payload.date

    db.add(row)
    db.commit()
    db.refresh(row)

    return row


@app.get(
    "/commandes",
    response_model=List[CommandeOut],
)
def list_commandes(
    db: Session = Depends(get_db),
    phone: Optional[str] = Query(
        default=None,
        description="Search using phone 1 or phone 2",
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=1000,
    ),
):
    query = db.query(Commande).order_by(
        desc(Commande.date),
        desc(Commande.id),
    )

    if phone and phone.strip():
        search_phone = f"%{phone.strip()}%"

        query = query.filter(
            or_(
                Commande.phone.ilike(search_phone),
                Commande.phone2.ilike(search_phone),
            )
        )

    return query.limit(limit).all()


@app.get(
    "/commandes/{commande_id}",
    response_model=CommandeOut,
)
def get_commande(
    commande_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
):
    row = (
        db.query(Commande)
        .filter(Commande.id == commande_id)
        .first()
    )

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Commande not found",
        )

    return row


@app.put(
    "/commandes/{commande_id}",
    response_model=CommandeOut,
)
def update_commande(
    payload: CommandeUpdate,
    commande_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
):
    row = (
        db.query(Commande)
        .filter(Commande.id == commande_id)
        .first()
    )

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Commande not found",
        )

    # Only fields sent by Angular are updated.
    update_data = payload.model_dump(exclude_unset=True)

    if "client_name" in update_data:
        value = update_data["client_name"]

        if value is not None:
            row.client_name = value.strip()

    if "phone" in update_data:
        value = update_data["phone"]

        if value is not None:
            row.phone = value.strip()

    if "phone2" in update_data:
        value = update_data["phone2"]

        # Allows the user to remove phone 2.
        row.phone2 = value.strip() or None if value else None

    if "address" in update_data:
        value = update_data["address"]

        if value is not None:
            row.address = value.strip()

    if "commande" in update_data:
        value = update_data["commande"]

        if value is not None:
            row.commande = value.strip()

    if "date" in update_data:
        value = update_data["date"]

        if value is not None:
            row.date = value

    db.commit()
    db.refresh(row)

    return row


@app.delete("/commandes/{commande_id}")
def delete_commande(
    commande_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
):
    row = (
        db.query(Commande)
        .filter(Commande.id == commande_id)
        .first()
    )

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Commande not found",
        )

    db.delete(row)
    db.commit()

    return {
        "ok": True,
        "deleted_id": commande_id,
    }