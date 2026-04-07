import asyncio
import logging
import json
from client import EnvClient
from models import CodeReviewAction, Comment

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("baseline_mock")

ENV_URL = "ws://localhost:7860/ws"

async def run_baseline():
    logger.info("START")
    env_client = EnvClient(uri=ENV_URL)
    await env_client.connect()
    
    tasks = ["task_easy", "task_medium", "task_hard"]
    total_score = 0.0
    
    # Pre-defined "perfect" answers to demonstrate the environment works
    mock_responses = {
        "task_easy": CodeReviewAction(
            comments=[Comment(line_number=2, issue="subtraction instead of addition", severity="high")],
            decision="request_changes"
        ),
        "task_medium": CodeReviewAction(
            comments=[Comment(line_number=3, issue="os.system command injection", severity="critical")],
            decision="request_changes"
        ),
        "task_hard": CodeReviewAction(
            comments=[Comment(line_number=6, issue="insecure pickle deserialization", severity="critical")],
            decision="request_changes"
        )
    }
    
    for task_id in tasks:
        logger.info(f"STEP: Resetting environment for {task_id}")
        obs = await env_client.reset(task_id=task_id)
        
        logger.info(f"STEP: Using mock action for {task_id}")
        action = mock_responses[task_id]
        
        logger.info(f"STEP: Submitting action for {task_id}")
        res = await env_client.step(action)
        reward = res.get('reward', 0.0)
        total_score += reward
        logger.info(f"STEP: {task_id} completed. Reward: {reward}")

    avg_score = total_score / len(tasks)
    logger.info(f"STEP: Final Average Score: {avg_score}")
    
    await env_client.close()
    logger.info("END")

if __name__ == "__main__":
    asyncio.run(run_baseline())
