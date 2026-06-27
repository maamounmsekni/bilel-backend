from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import declarative_base


Base = declarative_base()


def utcnow():
    return datetime.now(timezone.utc)


class Commande(Base):
    __tablename__ = "commandes"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    client_name = Column(
        String(200),
        nullable=False,
    )

    # Main telephone number
    phone = Column(
        String(50),
        nullable=False,
        index=True,
    )

    # Optional second telephone number
    phone2 = Column(
        String(50),
        nullable=True,
        index=True,
    )

    address = Column(
        String(255),
        nullable=False,
    )

    commande = Column(
        Text,
        nullable=False,
    )

    date = Column(
        DateTime(timezone=True),
        nullable=False,
        default=utcnow,
    )