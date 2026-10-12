from dataclasses import replace

import pytest
from temporalio.testing import ActivityEnvironment

from temporal_ecommerce.activities import (
    charge_customer_card,
    send_confirmation_email,
    update_inventory_database,
)
from temporal_ecommerce.models import OrderInput


async def test_charge_customer_card():
    env = ActivityEnvironment()

    order = OrderInput(
        order_id="CHARGE-TEST-1",
        customer_id="CHARGE-CUST-1",
        email="test@example.com",
        amount_cents=2500
    )

    with pytest.raises(RuntimeError):
        await env.run(charge_customer_card, order)

    env.info = replace(env.info, attempt=3)
    result = await env.run(charge_customer_card, order)
    assert result == f"ch_credit_card_company_{order.order_id}"


async def test_update_inventory_database():
    env = ActivityEnvironment()

    order = OrderInput(
        order_id="INVENTORY-TEST-1",
        customer_id="INVENTORY-CUST-1",
        email="test@example.com",
        amount_cents=2500
    )

    result = await env.run(update_inventory_database, order)
    assert result == True


async def test_send_confirmation_email():
    env = ActivityEnvironment()

    order = OrderInput(
        order_id="SEND-TEST-1",
        customer_id="SEND-CUST-1",
        email="test@example.com",
        amount_cents=2500
    )

    result = await env.run(send_confirmation_email, order)
    assert result == True
