from typing import List, Dict, Any
from .models import Reward, Action

class Task:
    def __init__(self, id: str, name: str, description: str, difficulty: str):
        self.id = id
        self.name = name
        self.description = description
        self.difficulty = difficulty

    def grade(self, history: List[Action]) -> Reward:
        raise NotImplementedError()

class RefundRequestTask(Task):
    def __init__(self):
        super().__init__("refund-request", "Refund Eligibility Check", "A customer asks for a refund for a 'Deluxe' subscription. Verify their eligibility based on the purchase date (within 30 days) and respond accordingly.", "Easy")

    def grade(self, history: List[Action]) -> Reward:
        score = 0.0
        details = []

        # Check if they looked up the ticket
        has_looked_at_ticket = any(a.action_type == "GetTicketDetails" and a.params.get("ticket_id") == "T-101" for a in history)
        if has_looked_at_ticket: score += 0.2; details.append("Looked at ticket.")

        # Check if they searched the customer
        has_searched_customer = any(a.action_type == "SearchCustomer" and a.params.get("email") == "customer1@example.com" for a in history)
        if has_searched_customer: score += 0.2; details.append("Searched customer CRM.")

        # Check if they replied with correct info
        replies = [a for a in history if a.action_type == "SendReply" and a.params.get("ticket_id") == "T-101"]
        correct_reply = any("refund" in r.params.get("message", "").lower() and "confirm" in r.params.get("message", "").lower() for r in replies)
        if correct_reply: score += 0.4; details.append("Sent correct refund confirmation.")

        # Check if they closed the ticket
        closed = any(a.action_type == "CloseTicket" and a.params.get("ticket_id") == "T-101" for a in history)
        if closed: score += 0.2; details.append("Closed the ticket.")

        return Reward(value=score, comment=", ".join(details))

class TechTroubleshootingTask(Task):
    def __init__(self):
        super().__init__("tech-troubleshoot", "Technical Troubleshooting", "A customer experiences a login error. Check their history in the CRM and provide the previously successful resolution.", "Medium")

    def grade(self, history: List[Action]) -> Reward:
        score = 0.0
        details = []

        has_searched = any(a.action_type == "SearchCustomer" and a.params.get("email") == "customer2@example.com" for a in history)
        if has_searched: score += 0.3; details.append("Checked customer history.")

        replies = [a for a in history if a.action_type == "SendReply" and a.params.get("ticket_id") == "T-102"]
        correct_reply = any("cache" in r.params.get("message", "").lower() for r in replies)
        if correct_reply: score += 0.5; details.append("Provided 'clear cache' solution.")

        closed = any(a.action_type == "CloseTicket" and a.params.get("ticket_id") == "T-102" for a in history)
        if closed: score += 0.2; details.append("Resolved ticket.")

        return Reward(value=score, comment=", ".join(details))

class ComplexMultiTicketTask(Task):
    def __init__(self):
        super().__init__("complex-multi-ticket", "Duplicate Ticket Resolution", "A customer has opened two tickets for the same missing item. Identify the duplicates, resolve both, and handle the customer's frustration professionally.", "Hard")

    def grade(self, history: List[Action]) -> Reward:
        score = 0.0
        details = []

        # Identified both tickets
        has_103 = any(a.action_type == "GetTicketDetails" and a.params.get("ticket_id") == "T-103" for a in history)
        has_104 = any(a.action_type == "GetTicketDetails" and a.params.get("ticket_id") == "T-104" for a in history)
        if has_103 and has_104: score += 0.2; details.append("Identified both related tickets.")

        # Professional reply (polite check)
        replies = [a for a in history if a.action_type == "SendReply"]
        polite = any("sorry" in r.params.get("message", "").lower() or "apologize" in r.params.get("message", "").lower() for r in replies)
        if polite: score += 0.2; details.append("Used professional/empathetic tone.")

        # Resolved both
        closed_103 = any(a.action_type == "CloseTicket" and a.params.get("ticket_id") == "T-103" for a in history)
        closed_104 = any(a.action_type == "CloseTicket" and a.params.get("ticket_id") == "T-104" for a in history)
        if closed_103 and closed_104: score += 0.6; details.append("Closed both duplicate tickets.")

        return Reward(value=score, comment=", ".join(details))

TASK_MAP = {
    "refund-request": RefundRequestTask,
    "tech-troubleshoot": TechTroubleshootingTask,
    "complex-multi-ticket": ComplexMultiTicketTask
}
