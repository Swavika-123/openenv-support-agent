from fastapi import FastAPI, HTTPException, Body
from .models import Action, Observation, Reward, EpisodeState, StepResponse
from .env import SupportAgentEnv
from .tasks import TASK_MAP

app = FastAPI(title="OpenEnv: Support Agent")
env = SupportAgentEnv()

@app.post("/reset", response_model=Observation)
async def reset(task_id: str = "refund-request"):
    try:
        return env.reset(task_id=task_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/step", response_model=StepResponse)
async def step(action: Action):
    # Process the step
    obs, reward, done, info = env.step(action)
    return StepResponse(
        observation=obs,
        reward=reward.value,
        done=done,
        info=info
    )

@app.get("/state", response_model=EpisodeState)
async def state():
    return env.state()

@app.get("/tasks")
async def list_tasks():
    return [
        {"id": tid, "name": t().name, "difficulty": t().difficulty}
        for tid, t in TASK_MAP.items()
    ]

@app.get("/")
async def root():
    return {"status": "online", "env": "SupportAgentEnv"}
