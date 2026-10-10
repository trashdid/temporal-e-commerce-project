from pydantic import BaseModel


class OrderInput(BaseModel):
    order_id: str
    customer_id: str
    email: str
    amount_cents: int
