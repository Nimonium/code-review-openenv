import random
from typing import Optional, Any
from openenv.core.env_server import Environment

from models import CodeReviewAction, CodeReviewObservation, CodeReviewState
from server.tasks import TASKS
from server.grader import DeterministicGrader

class CodeReviewEnvironment(Environment[CodeReviewAction, CodeReviewObservation, CodeReviewState]):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.grader = DeterministicGrader()
        self.current_state = None
        self.is_done = True
        
    def reset(self, seed: Optional[int] = None, episode_id: Optional[str] = None, task_id: str = None, **kwargs: Any) -> CodeReviewObservation:
        self._reset_rubric()
        if task_id and task_id in TASKS:
            task = TASKS[task_id]
        else:
            task = random.choice(list(TASKS.values()))
            
        self.current_state = CodeReviewState(
            episode_id=episode_id or "default",
            step_count=0,
            **task
        )
        self.is_done = False
        
        obs = CodeReviewObservation(
            code_snippet=self.current_state.code_snippet,
            task_id=self.current_state.task_id
        )
        return self._apply_transform(obs)

    def step(self, action: CodeReviewAction, timeout_s: Optional[float] = None, **kwargs: Any) -> CodeReviewObservation:
        if self.is_done:
            raise ValueError("Episode already done. Please reset.")
            
        self.current_state.step_count += 1
        score = self.grader.evaluate(self.current_state, action)
        self.is_done = True
        
        obs = CodeReviewObservation(
            code_snippet=self.current_state.code_snippet,
            task_id=self.current_state.task_id,
            done=True,
            reward=score
        )
        return self._apply_transform(obs)
        
    @property
    def state(self) -> CodeReviewState:
        if not self.current_state:
            raise ValueError("Environment not initialized. Please reset.")
        return self.current_state