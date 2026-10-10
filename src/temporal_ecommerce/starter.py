import asyncio
import os

from temporalio.client import Client
from temporalio.contrib.pydantic import pydantic_data_converter

from temporal_ecommerce.models import OrderInput
from temporal_ecommerce.workflows import ProcessOrderWorkflow


async def main():
    temporal_address = os.getenv("TEMPORAL_ADDRESS", "localhost:7233")
    client = await Client.connect(temporal_address, data_converter=pydantic_data_converter)

    order = OrderInput(
        order_id="ORD_1001",
        customer_id="CUST-42",
        email="customer@example.com",
        amount_cents=4999
    )

    print(f"Submitting order {order.order_id} to Temporal...")
    result = await client.execute_workflow(
        ProcessOrderWorkflow.run,
        order,
        id=f"order-process-{order.order_id}",
        task_queue="ecommerce-order-tasks"
    )
    print(f"Workflow result: {result}")


if __name__ == "__main__":
    asyncio.run(main())
