import asyncio
import logging
import os
import json
from openai import OpenAI
from client import EnvClient
from models import CodeReviewAction, Comment

# --- Configuration ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-api-key")
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
ENV_URL = os.getenv("ENV_URL", "ws://localhost:7860/ws")

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("baseline")

client_llm = OpenAI(api_key=OPENAI_API_KEY, base_url=API_BASE_URL)

async def run_baseline():
    logger.info("START")
    env_client = EnvClient(uri=ENV_URL)
    await env_client.connect()
    
    tasks = ["task_easy", "task_medium", "task_hard"]
    total_score = 0.0
    
    for task_id in tasks:
        logger.info(f"STEP: Resetting environment for {task_id}")
        obs = await env_client.reset(task_id=task_id)
        code = obs['code_snippet']
        
        logger.info(f"STEP: Prompting LLM for {task_id}")
        
        prompt = f"""
        You are a professional security auditor and code reviewer.
        Review the following Python code snippet and identify any bugs or security vulnerabilities.
        
        CODE:
        {code}
        
        Output your review as a JSON object matching this schema:
        {{
            "comments": [
                {{
                    "line_number": int,
                    "issue": "description",
                    "severity": "low" | "medium" | "high" | "critical"
                }}
            ],
            "decision": "approve" | "request_changes"
        }}
        """
        
        response = client_llm.chat.completions.create(
            model="gpt-4-turbo-preview", # or any suitable model
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        action_data = json.loads(response.choices[0].message.content)
        action = CodeReviewAction(**action_data)
        
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
    if OPENAI_API_KEY == "your-api-key":
        logger.warning("Warning: OPENAI_API_KEY not set. This script will likely fail.")
    asyncio.run(run_baseline())