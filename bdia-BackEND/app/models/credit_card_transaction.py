from sqlalchemy import Column, Integer, Float, Boolean, DateTime
from .base import Base
from datetime import datetime
from sqlalchemy.sql import func

class CreditCardTransaction(Base):
    __tablename__ = "credit_card_transactions"

    id = Column(Integer, primary_key=True, index=True)
    time = Column(Float, nullable=False)  # Secondes depuis la première transaction
    v1 = Column(Float, nullable=False)
    v2 = Column(Float, nullable=False)
    v3 = Column(Float, nullable=False)
    v4 = Column(Float, nullable=False)
    v5 = Column(Float, nullable=False)
    v6 = Column(Float, nullable=False)
    v7 = Column(Float, nullable=False)
    v8 = Column(Float, nullable=False)
    v9 = Column(Float, nullable=False)
    v10 = Column(Float, nullable=False)
    v11 = Column(Float, nullable=False)
    v12 = Column(Float, nullable=False)
    v13 = Column(Float, nullable=False)
    v14 = Column(Float, nullable=False)
    v15 = Column(Float, nullable=False)
    v16 = Column(Float, nullable=False)
    v17 = Column(Float, nullable=False)
    v18 = Column(Float, nullable=False)
    v19 = Column(Float, nullable=False)
    v20 = Column(Float, nullable=False)
    v21 = Column(Float, nullable=False)
    v22 = Column(Float, nullable=False)
    v23 = Column(Float, nullable=False)
    v24 = Column(Float, nullable=False)
    v25 = Column(Float, nullable=False)
    v26 = Column(Float, nullable=False)
    v27 = Column(Float, nullable=False)
    v28 = Column(Float, nullable=False)
    amount = Column(Float, nullable=False)
    is_fraud = Column(Boolean, nullable=False, default=False)  # True = fraude
    created_at = Column(DateTime, nullable=False, default=func.now())