from pydantic import BaseModel
from typing import Optional

class TransactionInput(BaseModel):
    transaction_id: str
    user_id: str
    banque_id: Optional[str]
    transaction_amount: float
    account_balance: float
    transaction_category: str  # "achat", "retrait", "virement"
    balance_change: float
    is_new_user: int
