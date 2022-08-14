import datetime
import uuid

from pydantic import BaseModel


class Confirmation(BaseModel):
    confirmation_url: str
    type: str


class Amount(BaseModel):
    currency: str
    value: float


class YooPayment(BaseModel):
    id: uuid.UUID
    amount: Amount
    description: str
    created_at: datetime.datetime
    confirmation: Confirmation | None
    paid: bool
    status: str

    def is_paid(self) -> bool:
        return self.paid
