# app/models/alert.py

from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False)
    banque_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    fraud_probability = Column(Float)
    message = Column(String)
    status = Column(String, default="non traité")
    date = Column(DateTime, default=datetime.utcnow)

    transaction = relationship("Transaction", backref="alert")
    banque = relationship("User", backref="alerts")
