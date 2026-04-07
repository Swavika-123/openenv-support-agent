from typing import Dict, Any, List, Optional
from .models import Observation, Action, Reward, EpisodeState
from .data import TICKETS, CUSTOMERS
from .tasks import TASK_MAP

class SupportAgentEnv:
    def __init__(self):
        self.current_task_id: Optional[str] = None
        self.history: List[Action] = []
        self.step_count = 0
        self.max_steps = 15
        self.done = False
        self.cumulative_score = 0.0

    def reset(self, task_id: str = "refund-request") -> Observation:
        if task_id not in TASK_MAP:
            raise ValueError(f"Unknown task: {task_id}")

        self.current_task_id = task_id
        self.history = []
        self.step_count = 0
        self.done = False
        self.cumulative_score = 0.0

        # Build initial observation
        task_desc = TASK_MAP[task_id]().description
        return Observation(
            view=f"Task Started: {task_id}\nDescription: {task_desc}\nYou are logged into the Support Agent Terminal.\nAvailable Actions: ListTickets, GetTicketDetails, SearchCustomer, SendReply, EscalateTicket, CloseTicket.",
            data={"task_id": task_id, "status": "Ready"},
            done=False
        )

    def step(self, action: Action) -> (Observation, Reward, bool, Dict[str, Any]):
        if self.done:
            return Observation(view="Episode already finished.", done=True), Reward(value=0.0, comment="Episode finished."), True, {}

        self.history.append(action)
        self.step_count += 1

        result_view = ""
        result_data = {}

        if action.action_type == "ListTickets":
            result_view = "Tickets:\n" + "\n".join([f"ID: {tid} | Subject: {t['subject']} | Email: {t['email']}" for tid, t in TICKETS.items()])
            result_data = {"tickets": TICKETS}
        elif action.action_type == "GetTicketDetails":
            tid = action.params.get("ticket_id")
            ticket = TICKETS.get(tid)
            if ticket:
                result_view = f"Ticket {tid}:\nSubject: {ticket['subject']}\nEmail: {ticket['email']}\nMessage: {ticket['message']}"
                result_data = {"ticket": ticket}
            else:
                result_view = f"Ticket {tid} not found."
        elif action.action_type == "SearchCustomer":
            email = action.params.get("email")
            cust = next((c for cid, c in CUSTOMERS.items() if c["email"] == email), None)
            if cust:
                result_view = f"Customer Profile: {cust['name']}\nEmail: {cust['email']}\nSubscription: {cust['subscription']}\nPurchase Date: {cust['purchase_date']}\nHistory: {cust.get('history', []) or cust.get('order_history', [])}"
                result_data = {"customer": cust}
            else:
                result_view = f"Customer with email {email} not found."
        elif action.action_type == "SendReply":
            tid = action.params.get("ticket_id")
            msg = action.params.get("message")
            result_view = f"Sent reply to {tid}: {msg}"
            result_data = {"status": "sent"}
        elif action.action_type == "EscalateTicket":
            tid = action.params.get("ticket_id")
            result_view = f"Ticket {tid} escalated."
            result_data = {"status": "escalated"}
        elif action.action_type == "CloseTicket":
            tid = action.params.get("ticket_id")
            result_view = f"Ticket {tid} closed."
            result_data = {"status": "closed"}
            # Finishing logic could be triggered by closing a ticket, or by reaching max steps
            # In some cases, multiple tickets might need to be closed.

        # Calculate reward: The improvement in score from the total history
        total_score_reward = TASK_MAP[self.current_task_id]().grade(self.history)
        delta_reward = total_score_reward.value - self.cumulative_score
        
        # Add a small step penalty to discourage infinite loops and encourage efficiency
        delta_reward -= 0.01
        
        self.cumulative_score = total_score_reward.value

        if self.step_count >= self.max_steps:
            self.done = True

        if self.done:
            result_view += f"\n\nEPISODE ENDED. Final Score: {self.cumulative_score}. Reason: {total_score_reward.comment}"
            return Observation(view=result_view, data=result_data, done=True), Reward(value=delta_reward, comment=total_score_reward.comment), True, {}

        return Observation(view=result_view, data=result_data, done=False), Reward(value=delta_reward, comment=total_score_reward.comment), False, {}

    def state(self) -> EpisodeState:
        return EpisodeState(
            task_id=self.current_task_id or "not_started",
            step_count=self.step_count,
            max_steps=self.max_steps,
            metadata={"history_len": len(self.history)}
        )
