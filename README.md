# OpenEnv: Support Agent Environment

A production-grade OpenEnv implementation simulating a **Customer Support Representative** workstation. Agents must resolve customer tickets by querying a mock CRM, checking interaction history, and providing technical or policy-based resolutions.

## Environment Overview

- **Real-World Task**: Customer Support Ticket Triage and Resolution.
- **Spec Compliance**: Full OpenEnv interface (`reset`, `step`, `state`) using FastAPI and Pydantic.
- **Deployment**: Ready for Hugging Face Spaces with included Dockerfile.
- **Motivation**: This environment aims to benchmark AI agents on tasks involving multi-step reasoning, data retrieval from mixed sources (CRM + Tickets), and professional communication—essential skills for modern agentic workflows.

### Action Space

| Action              | Parameters                      | Description                                                                 |
|---------------------|---------------------------------|-----------------------------------------------------------------------------|
| `ListTickets`       | `{}`                            | List all open tickets with their IDs and subjects.                          |
| `GetTicketDetails`  | `{"ticket_id": str}`            | Read the message content and metadata of a specific ticket.                 |
| `SearchCustomer`    | `{"email": str}`                | Retrieve customer profile, subscription status, and history from the CRM.   |
| `SendReply`         | `{"ticket_id": str, "msg": str}`| Send a message to the customer.                                             |
| `EscalateTicket`    | `{"ticket_id": str, "reason": str}`| Move the ticket to a human specialist.                                     |
| `CloseTicket`       | `{"ticket_id": str}`            | Mark the ticket as resolved.                                               |

### Observation Space

The observation is a JSON object with:
- `view`: A textual description of the action's result (human-readable for the agent).
- `data`: Structured dictionary containing raw entity data (e.g., ticket data, customer data).
- `done`: Boolean flag indicating if the episode has ended.

## Tasks

1.  **Refund Eligibility Check (Easy, ID: `refund-request`)**:
    - **Goal**: Validate if a customer is within the 30-day refund window.
    - **Reward**: 1.0 (Full completion), 0.0-0.8 (Partial progress like reading ticket/searching CRM).

2.  **Technical Troubleshooting (Medium, ID: `tech-troubleshoot`)**:
    - **Goal**: Check customer history to find a resolution for a known technical error.
    - **Reward**: 1.0 (Providing the specific 'clear cache' solution from history).

3.  **Duplicate Ticket Management (Hard, ID: `complex-multi-ticket`)**:
    - **Goal**: Identify and resolve two related tickets from the same customer while maintaining a professional tone.
    - **Reward**: 1.0 (Resolving both tickets politely).

## Setup & Usage

### Local Execution (with Docker)

1.  **Build the container**:
    ```bash
    docker build -t openenv-support-agent .
    ```

2.  **Run the environment**:
    ```bash
    docker run -p 7860:7860 openenv-support-agent
    ```

3.  **Run Inference**:
    Ensure you have your environment variables set:
    ```bash
    export OPENAI_API_KEY="your-key"
    export API_BASE_URL="https://api.openai.com/v1"
    export MODEL_NAME="gpt-4o-mini"
    python inference.py
    ```

### Hugging Face Spaces Deployment

The environment can be deployed directly using the provided `hf_upload.py` script:

1.  **Set your HF Token**:
    ```bash
    export HF_TOKEN="your_hugging_face_token"
    ```

2.  **Deploy**:
    ```bash
    python hf_upload.py --repo "your-username/openenv-support-agent"
    ```

## Mandatory STDOUT Format (`inference.py`)

The inference script produces the following telemetry:

- `[START]`: task metadata.
- `[STEP]`: Action trace with rewards (0.00-1.00).
- `[END]`: Episode success (true/false), step count, and per-step rewards.

## Baseline Performance

| Task                          | Model         | Score | Steps |
|-------------------------------|---------------|-------|-------|
| Refund Eligibility Check      | GPT-4o-mini   | 1.00  | 4     |
| Technical Troubleshooting     | GPT-4o-mini   | 1.00  | 3     |
| Duplicate Ticket Management   | GPT-4o-mini   | 0.80  | 6     |

## Metadata (openenv.yaml)
Standard OpenEnv metadata for automated benchmarking.
