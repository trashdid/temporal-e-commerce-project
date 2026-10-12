from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

from ..models import OrderInput

with workflow.unsafe.imports_passed_through():
    from ..activities import (
        charge_customer_card,
        send_confirmation_email,
        update_inventory_database,
    )


@workflow.defn
class ProcessOrderWorkflow:
    @workflow.run
    async def run(self, order: OrderInput) -> str:
        payment_retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=1),
            backoff_coefficient=2.0,
            maximum_interval=timedelta(seconds=10),
            maximum_attempts=5
        )

        payment_id = await workflow.execute_activity(
            charge_customer_card,
            order,
            start_to_close_timeout=timedelta(seconds=10),
            retry_policy=payment_retry_policy
        )

        await workflow.execute_activity(
            update_inventory_database,
            order,
            start_to_close_timeout=timedelta(seconds=10)
        )

        await workflow.execute_activity(
            send_confirmation_email,
            order,
            start_to_close_timeout=timedelta(seconds=10)
        )

        return f"Order {order.order_id} processed successfully with payment {payment_id}."
