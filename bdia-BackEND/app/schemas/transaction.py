from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TransactionBase(BaseModel):
    customer_id: int
    customer_name: str
    gender: str
    age: int
    state: str
    city: str
    bank_branch: str
    account_type: str
    transaction_id: int
    transaction_date: datetime
    transaction_time: str
    transaction_amount: float
    merchant_id: int
    transaction_type: str
    merchant_category: str
    account_balance: float
    transaction_device: str
    transaction_location: str
    device_type: str
    transaction_currency: str
    customer_contact: str
    transaction_description: str
    customer_email: str
    banque_id: int  # Relier à la banque (FK vers users.id)

    # Champs ajoutés par le système de prédiction
    is_fraud: Optional[bool] = None
    fraud_probability: Optional[float] = None

class TransactionCreate(TransactionBase):
    pass

class TransactionRead(TransactionBase):
    id: int  # Clé primaire SQL

    class Config:
        from_attributes = True

class TransactionUpdate(BaseModel):
    customer_id: Optional[int] = None
    customer_name: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    state: Optional[str] = None
    city: Optional[str] = None
    bank_branch: Optional[str] = None
    account_type: Optional[str] = None
    transaction_id: Optional[int] = None
    transaction_date: Optional[datetime] = None
    transaction_time: Optional[str] = None
    transaction_amount: Optional[float] = None
    merchant_id: Optional[int] = None
    transaction_type: Optional[str] = None
    merchant_category: Optional[str] = None
    account_balance: Optional[float] = None
    transaction_device: Optional[str] = None
    transaction_location: Optional[str] = None
    device_type: Optional[str] = None
    transaction_currency: Optional[str] = None
    customer_contact: Optional[str] = None
    transaction_description: Optional[str] = None
    customer_email: Optional[str] = None
    banque_id: Optional[int] = None
    is_fraud: Optional[bool] = None
    fraud_probability: Optional[float] = None

    class Config:
        from_attributes = True