# app/schemas/alert.py

from pydantic import BaseModel
from datetime import datetime

class AlertCreate(BaseModel):
    transaction_id: int
    banque_id: int
    fraud_probability: float
    message: str

class AlertRead(AlertCreate):
    id: int
    date: datetime
    status: str

    class Config:
       from_attributes = True
