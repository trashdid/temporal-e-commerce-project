# Temporal E-Commerce: Distributed Order Processing Engine

A durable execution engine demonstrating resilient, fault-tolerant distributed transaction orchestration using **Temporal** and **Python 3.14**.

This project implements an end-to-end e-commerce order fulfillment pipeline, progressing from basic synchronous orchestration to distributed sagas, idempotency, and human-in-the-loop workflows.

While inspired by the core patterns in [Temporal's Money Transfer Project Template](https://github.com/temporalio/money-transfer-project-template-python), this implementation expands beyond a two-step transfer into an enterprise-style e-commerce fulfillment pipeline with human-in-the-loop signals, live queries, long-running timers, and multi-step distributed saga compensations.


---

## 💡 Why Temporal? (The Architectural Problem)

In traditional microservice architectures, orchestrating multi-step business transactions (billing, inventory, shipping, notifications) is brittle:
- **Point-to-point HTTP calls** fail mid-flight, leaving data in inconsistent states.
- **Message queues & Cron jobs** require complex dead-letter queues (DLQs), deduplication, and external state tracking in databases or Redis.
- **Distributed transactions (2PC)** introduce tight coupling and latency bottlenecks.

### The Temporal Solution: Durable Execution
Temporal shifts reliability from application code to the orchestration platform:
- **Deterministic Workflows:** Workflow state is recorded as an immutable sequence of events in an **Event History**. If a worker crashes or restarts, Temporal replays past events to seamlessly resume execution at the exact point of interruption without repeating completed external side-effects.
- **Decoupled Activities:** Non-deterministic side effects (Stripe, SendGrid, database updates) run in isolated Activities with native retry policies, timeouts, and idempotency guarantees.

---

## 🗺️ Project Architecture & Learning Roadmap

This project is built across 4 progressive phases:

```
[Client / Starter]
       │
       ▼ (Workflow Start)
┌─────────────────────────────────────────────────────────────┐
│                   ProcessOrderWorkflow                      │
│                                                             │
│  Phase 1: ChargeCustomerCard ──► UpdateInventory ──► Email  │
│                                                             │
│  Phase 2: Transient Failures & Idempotency Key Handling     │
│                                                             │
│  Phase 3: Fraud Review (> $1,000) ──► Signal / 24h Timer    │
│                                                             │
│  Phase 4: Distributed Saga Rollback (Refund & Restock)      │
└─────────────────────────────────────────────────────────────┘
```

- [x] **Phase 1: The Foundation (Basic Execution)**
  - Separation of concerns: Deterministic workflow orchestration vs. activity execution.
  - Asynchronous task queues and pull-based worker polling.
  - End-to-end test suite using Temporal's in-memory `WorkflowEnvironment`.
- [ ] **Phase 2: Fault Tolerance & Idempotency**
  - Simulated transient network faults (Stripe timeouts).
  - Exponential backoff & jitter with custom `RetryPolicy`.
  - Idempotency key pattern to prevent duplicate charges across retries.
- [ ] **Phase 3: Human-in-the-Loop (Signals & Queries)**
  - Long-running paused workflows awaiting external human authorization (> $1,000 orders).
  - External inspection via **Queries** (read-only state reflection).
  - External mutation via **Signals** (approvals/rejections).
  - Durable timers with automated fallback actions (24-hour timeout auto-cancel).
- [ ] **Phase 4: The Distributed Saga (Compensation Pattern)**
  - Compensating transactions to safely reverse distributed state upon fatal errors.
  - Automatic rollback (`RefundCustomerCard` & `RestockInventory`) when downstream fulfillment fails.

---

## 📁 Project Structure

```text
temporal-ecommerce/
├── src/
│   └── temporal_ecommerce/
│       ├── activities/            # Non-deterministic side effects (APIs, DBs)
│       │   ├── charge_customer_card.py
│       │   ├── send_confirmation_email.py
│       │   └── update_inventory_database.py
│       ├── workflows/             # Deterministic orchestration logic
│       │   └── process_order_workflow.py
│       ├── models/                # Typed domain models (Pydantic)
│       │   └── order_input.py
│       ├── worker.py              # Long-running worker process polling task queues
│       └── starter.py             # Client script initiating order workflows
├── tests/                         # Pytest test suite with time-skipping
│   ├── test_activities.py         # Activity unit tests using ActivityEnvironment
│   └── test_workflows.py          # End-to-end workflow integration tests
├── .devcontainer/                 # Dev Container with Python 3.14 & Temporal server
├── pyproject.toml                 # UV project configuration and dependencies
└── README.md
```

---

## 🚀 Quickstart & How to Run

### Prerequisites
- Python 3.14+
- [`uv`](https://docs.astral.sh/uv/) package manager
- Docker (for the Temporal development server)

### 1. Install Dependencies
```bash
uv sync
```

### 2. Verify Temporal Server
The local Temporal server runs via Docker:
- **Temporal Frontend gRPC:** `localhost:7233` (or `temporal:7233` inside dev container)
- **Temporal Web UI:** `http://localhost:8233`

### 3. Run the Worker
Start the worker listening for order tasks:
```bash
uv run python -m temporal_ecommerce.worker
```

### 4. Trigger an Order Execution
In a separate terminal, trigger a test order:
```bash
uv run python -m temporal_ecommerce.starter
```

### 5. Inspect the Execution in the Web UI
Open **[http://localhost:8233](http://localhost:8233)** to view:
- **Execution Timeline:** Visual step-by-step progress.
- **Event History:** The exact record of state transitions (`WorkflowTaskScheduled`, `ActivityTaskCompleted`, etc.).

---

## 🧪 Automated Testing

This project leverages Temporal's built-in in-memory testing server with **time-skipping**:

```bash
uv run pytest
```

- **Activity Tests:** Validates individual activity logic in isolation using `ActivityEnvironment`.
- **Workflow Tests:** Runs full integration tests with an ephemeral test worker using `WorkflowEnvironment.start_time_skipping()`.

---

## 📚 Architectural Lineage & References

This project synthesizes canonical distributed systems literature and reference architectures into a practical evaluation benchmark:

1. **Temporal Reference Architectures:**
   - **[Money Transfer Sample](https://github.com/temporalio/money-transfer-project-template-python):** Baseline for state transitions, network timeout retries, and Stripe idempotency keys (Phases 1 & 2).
   - **[Trip Booking Saga Sample](https://github.com/temporalio/samples-python):** Foundational model for compensating transactions and failure recovery (Phase 4), adapted here into an e-commerce fulfillment flow.

2. **Distributed Systems Literature:**
   - **Chris Richardson (*Microservices Patterns* / [Microservices.io](https://microservices.io)):** The multi-step Order Management System is the industry benchmark for distributed transactions across bounded contexts (Billing, Inventory, and Fulfillment).

3. **The Cadence / Temporal Lineage:**
   - Temporal originates from **Cadence**, developed at Uber by Maxim Fateev and Samar Abbas to manage complex, stateful business processes (rider-driver matching, payment splitting, and physical-to-digital state machines). The human-in-the-loop fraud delay (Phase 3) mirrors these stateful workflows.

