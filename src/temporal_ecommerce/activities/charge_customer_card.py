import asyncio

from temporalio import activity

from ..models import OrderInput


@activity.defn
async def charge_customer_card(order: OrderInput) -> str:
    activity.logger.info(f"Charging customer {order.customer_id} ${order.amount_cents / 100:.2f} via Credit Card Company...")
    await asyncio.sleep(1)
    return f"fake_credit_card_company_ch_{order.order_id}"
