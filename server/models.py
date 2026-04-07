from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field

class Observation(BaseModel):
    view: str = Field(..., description="The textual view of the current state or result of the last action.")
    data: Dict[str, Any] = Field(default_factory=dict, description="Structured data returned from the action.")
    done: bool = Field(default=False, description="Whether the episode is finished.")

class Action(BaseModel):
    action_type: str = Field(..., description="Type of action: ListTickets, GetTicketDetails, SearchCustomer, SendReply, EscalateTicket, CloseTicket")
    params: Dict[str, Any] = Field(default_factory=dict, description="Parameters for the action.")

class Reward(BaseModel):
    value: float = Field(..., ge=0.0, le=1.0, description="The reward value between 0.0 and 1.0.")
    comment: str = Field(default="", description="Explanation of the reward.")

class EpisodeState(BaseModel):
    task_id: str
    step_count: int
    max_steps: int
    metadata: Dict[str, Any] = Field(default_factory=dict)

class StepResponse(BaseModel):
    observation: Observation
    reward: float
    done: bool
    info: Dict[str, Any] = Field(default_factory=dict)
