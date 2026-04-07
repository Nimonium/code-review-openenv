import logging
from openenv.core.env_server.http_server import create_fastapi_app

from server.environment import CodeReviewEnvironment
from models import CodeReviewAction, CodeReviewObservation
from server.tasks import TASKS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = create_fastapi_app(
    env=CodeReviewEnvironment,
    action_cls=CodeReviewAction,
    observation_cls=CodeReviewObservation
)

last_score = {"score": 0.0}

@app.get("/tasks")
def list_tasks():
    return {"tasks": list(TASKS.keys())}

@app.get("/grader")
def get_grader_score():
    return last_score

@app.post("/baseline")
def run_baseline():
    logger.info("START BASELINE")
    env_instance = CodeReviewEnvironment()
    obs = env_instance.reset(task_id="hard")
    
    logger.info(f"STEP: Observed snippet for {obs.task_id}")
    action = CodeReviewAction(
        comments=[{"line_number": 6, "issue": "insecure deserialization via pickle", "severity": "critical"}],
        decision="request_changes"
    )
    obs_next = env_instance.step(action)
    last_score["score"] = obs_next.reward
    logger.info(f"END: Score {last_score['score']}")
    env_instance.close()
    
    return {"status": "success", "score": obs_next.reward}