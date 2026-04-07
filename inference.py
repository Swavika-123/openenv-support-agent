import asyncio
import os
import json
import textwrap
from typing import List, Optional, Dict, Any
import httpx
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Configuration from environment
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    raise ValueError("HF_TOKEN environment variable is required")

# OpenEnv Environment URL (local FastAPI server)
ENV_API_URL = os.getenv("ENV_API_URL", "http://127.0.0.1:8000")

BENCHMARK = "support-agent-env"
MAX_STEPS = 10
TEMPERATURE = 0.0

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )

def log_end(success: bool, steps: int, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} rewards={rewards_str}", flush=True)

async def get_model_action(client: OpenAI, history: List[Dict[str, Any]], observation: str) -> Dict[str, Any]:
    system_prompt = textwrap.dedent(
        """
        You are a Customer Support AI Agent. Solve the task using the available actions.
        Available Actions: ListTickets, GetTicketDetails, SearchCustomer, SendReply, EscalateTicket, CloseTicket.
        
        Rules:
        1. Always respond with a valid JSON object: {"action_type": "...", "params": {...}}
        2. Keep messages professional.
        3. Search for customer info before making refund or technical decisions.
        """
    ).strip()

    messages = [{"role": "system", "content": system_prompt}]
    for h in history[-5:]:
        messages.append({"role": "user", "content": f"Action: {h['action']}\nObservation: {h['obs']}"})
    
    messages.append({"role": "user", "content": f"Current Observation: {observation}\n\nWhat is your next action?"})

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=TEMPERATURE,
            response_format={"type": "json_object"}
        )
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        return {"action_type": "ListTickets", "params": {}}

async def run_task(task_id: str):
    client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)
    
    async with httpx.AsyncClient() as env_client:
        log_start(task=task_id, env=BENCHMARK, model=MODEL_NAME)
        
        # Reset environment
        resp = await env_client.post(f"{ENV_API_URL}/reset?task_id={task_id}")
        obs_data = resp.json()
        
        history = []
        rewards = []
        steps_taken = 0
        done = False
        final_score = 0.0

        for step in range(1, MAX_STEPS + 1):
            try:
                action = await get_model_action(client, history, obs_data["view"])
                
                # Step environment
                step_resp = await env_client.post(f"{ENV_API_URL}/step", json=action)
                if step_resp.status_code != 200:
                    error_msg = step_resp.text
                    log_step(step=step, action=json.dumps(action), reward=0.0, done=False, error=error_msg)
                    break
                
                step_data = step_resp.json()
                
                reward = step_data.get("reward", 0.0)
                done = step_data.get("done", False)
                obs_view = step_data["observation"]["view"]
                
                log_step(step=step, action=json.dumps(action), reward=reward, done=done, error=None)
                
                rewards.append(reward)
                history.append({"action": action, "obs": obs_view})
                obs_data = step_data["observation"] # update for next step
                steps_taken = step
                final_score = max(final_score, step_data["reward"]) # Use raw reward if cumulative is handled by env

                if done:
                    break
            except Exception as e:
                log_step(step=step, action="error", reward=0.0, done=True, error=str(e))
                break
        
        success = final_score >= 0.8
        log_end(success=success, steps=steps_taken, rewards=rewards)

async def main():
    tasks = ["refund-request", "tech-troubleshoot", "complex-multi-ticket"]
    for task in tasks:
        try:
            await run_task(task)
        except Exception as e:
            print(f"[ERROR] Task {task} failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
