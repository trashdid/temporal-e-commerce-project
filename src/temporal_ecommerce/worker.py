import asyncio
import os

from temporalio.client import Client
from temporalio.contrib.pydantic import pydantic_data_converter
from temporalio.worker import Worker

from temporal_ecommerce.activities import (
    charge_customer_card,
    send_confirmation_email,
    update_inventory_database,
)
from temporal_ecommerce.workflows import ProcessOrderWorkflow

TASK_QUEUE = "ecommerce-order-tasks"

async def main():
    temporal_address = os.getenv("TEMPORAL_ADDRESS", "localhost:7233")
    client = await Client.connect(temporal_address, data_converter=pydantic_data_converter)

    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[ProcessOrderWorkflow],
        activities=[
            charge_customer_card,
            send_confirmation_email,
            update_inventory_database
        ],
    )

    print(f"Worker started, listening on task queue: '{TASK_QUEUE}'...")
    
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())