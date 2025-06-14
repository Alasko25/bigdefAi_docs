from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime, ForeignKey
from app.core.database import Base
from sqlalchemy.orm import relationship

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, index=True)  # Correspond à Customer_ID
    customer_name = Column(String)  # Customer_Name
    gender = Column(String)  # Gender
    age = Column(Integer)  # Age
    state = Column(String)  # State
    city = Column(String)  # City
    bank_branch = Column(String)  # Bank_Branch
    account_type = Column(String)  # Account_Type
    transaction_id = Column(Integer, index=True)  # Transaction_ID
    transaction_date = Column(DateTime)  # Transaction_Date
    transaction_time = Column(String)  # Transaction_Time (stocké comme string, par exemple "HH:MM:SS")
    transaction_amount = Column(Float)  # Transaction_Amount
    merchant_id = Column(Integer)  # Merchant_ID
    transaction_type = Column(String)  # Transaction_Type
    merchant_category = Column(String)  # Merchant_Category
    account_balance = Column(Float)  # Account_Balance
    transaction_device = Column(String)  # Transaction_Device
    transaction_location = Column(String)  # Transaction_Location
    device_type = Column(String)  # Device_Type
    is_fraud = Column(Boolean)  # Is_Fraud
    transaction_currency = Column(String)  # Transaction_Currency
    customer_contact = Column(String)  # Customer_Contact
    transaction_description = Column(String)  # Transaction_Description
    customer_email = Column(String)  # Customer_Email
    banque_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Relier à l'utilisateur banque

    # Champs pour la prédiction
    fraud_probability = Column(Float)  # Probabilité de fraude

    banque = relationship("User", backref="transactions_banque")