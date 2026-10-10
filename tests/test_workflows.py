from temporalio.contrib.pydantic import pydantic_data_converter
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from temporal_ecommerce.activities import (
    charge_customer_card,
    send_confirmation_email,
    update_inventory_database,
)
from temporal_ecommerce.models import OrderInput
from temporal_ecommerce.workflows import ProcessOrderWorkflow


async def test_process_order_workflow_success():
    async with await WorkflowEnvironment.start_time_skipping(data_converter=pydantic_data_converter) as env:
        task_queue = "test-ecommerce-tasks"

        async with Worker(
            env.client,
            task_queue=task_queue,
            workflows=[ProcessOrderWorkflow],
            activities=[
                charge_customer_card,
                update_inventory_database,
                send_confirmation_email
            ]
        ):
            order = OrderInput(
                order_id="ORD-TEST-99",
                customer_id="CUST-99",
                email="test@example.com",
                amount_cents=9900
            )

            result = await env.client.execute_workflow(
                ProcessOrderWorkflow.run,
                order,
                id=f"test-order-{order.order_id}",
                task_queue=task_queue
            )

            assert "ORD-TEST-99" in result
            assert "fake_credit_card_company_ch_ORD-TEST-99" in result
    