from unittest import result
from temporalio.contrib.pydantic import pydantic_data_converter
from temporalio.testing import ActivityEnvironment, WorkflowEnvironment
from temporalio.worker import Worker

from temporal_ecommerce.activities import(
    charge_customer_card,
    send_confirmation_email,
    update_inventory_database
)
from temporal_ecommerce.activities.charge_customer_card import MOCK_CREDIT_CARD_COMPANY_DB
from temporal_ecommerce.models import OrderInput
from temporal_ecommerce.workflows import ProcessOrderWorkflow


async def test_workflow_recovers_from_transient_failures():
    async with await WorkflowEnvironment.start_time_skipping(
        data_converter=pydantic_data_converter
    ) as env:
        task_queue = "phase2-test-tasks"

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
                order_id="ORD-RETRY-01",
                customer_id="CUST-RETRY-01",
                email="retry@example.com",
                amount_cents=7500
            )

            result = await env.client.execute_workflow(
                ProcessOrderWorkflow.run,
                order,
                id=f"test-retry-{order.order_id}",
                task_queue=task_queue
            )

            assert "ORD-RETRY-01" in result
            assert "ch_credit_card_company_ORD-RETRY-01" in result


async def test_activity_idempotency_prevents_double_billing():
    env = ActivityEnvironment()
    order = OrderInput(
        order_id="ORD-IDEM-01",
        customer_id="CUST-IDEM-01",
        email="idem@example.com",
        amount_cents=5000
    )

    idempotency_key = f"credit-card-idem-{order.order_id}"
    MOCK_CREDIT_CARD_COMPANY_DB[idempotency_key] = "ch_credit_card_company_already_charged"

    result = await env.run(charge_customer_card, order)

    assert result == "ch_credit_card_company_already_charged"