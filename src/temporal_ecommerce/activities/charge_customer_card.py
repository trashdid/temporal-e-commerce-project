import asyncio

from temporalio import activity

from ..models import OrderInput

MOCK_CREDIT_CARD_COMPANY_DB: dict[str, str] = {}

@activity.defn
async def charge_customer_card(order: OrderInput) -> str:
    attempt = activity.info().attempt
    idempotency_key = f"credit-card-idem-{order.order_id}"

    activity.logger.info(
        f"[Attempt {attempt}] Processing payment for order {order.order_id}"
        f"(${order.amount_cents / 100:.2f}) with idempotency key: {idempotency_key}"
    )

    if idempotency_key in MOCK_CREDIT_CARD_COMPANY_DB:
        existing_charge_id = MOCK_CREDIT_CARD_COMPANY_DB[idempotency_key]
        activity.logger.info(
            f"Idempotency hit! Order {order.order_id} was already charged."
            f"Returning existing charge ID: {existing_charge_id}"
        )
        return existing_charge_id
    
    if attempt < 3:
        activity.logger.warning(
            f"Simulated Network timeout connection to Credit Card Company gateway on attempt {attempt}!"
        )

        await asyncio.sleep(0.5)
        raise RuntimeError("Credit Card Company API connection timeout (attempt {attempt} failed)")
    
    charge_id = f"ch_credit_card_company_{order.order_id}"
    MOCK_CREDIT_CARD_COMPANY_DB[idempotency_key] = charge_id

    activity.logger.info(f"Payment succeeded on attempt {attempt}! Generated charge ID: {charge_id}")
    
    return charge_id
