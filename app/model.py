from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

def utcnow():
    return datetime.now(timezone.utc)

class Commande(Base):
    __tablename__ = "commandes"

    id = Column(Integer, primary_key=True, index=True)
    client_name = Column(String(200), nullable=False)
    phone = Column(String(50), nullable=False, index=True)
    address = Column(String(255), nullable=False)
    commande = Column(Text, nullable=False)
    date = Column(DateTime(timezone=True), nullable=False, default=utcnow)
