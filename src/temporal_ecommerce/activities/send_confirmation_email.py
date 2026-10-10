import asyncio

from temporalio import activity

from ..models import OrderInput


@activity.defn
async def send_confirmation_email(order: OrderInput) -> bool:
    activity.logger.info(f"Sending confirmation email to {order.email} via Email Service...")
    await asyncio.sleep(1)
    return True