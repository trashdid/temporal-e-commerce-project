import asyncio

from temporalio import activity

from ..models import OrderInput


@activity.defn
async def update_inventory_database(order: OrderInput) -> bool:
    activity.logger.info(f"Updating inventory datbase for {order.order_id}...")
    await asyncio.sleep(1)
    return True
