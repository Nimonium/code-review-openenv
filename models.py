from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from openenv.core.env_server import Action, Observation, State

class Comment(BaseModel):
    line_number: int = Field(description="The line number where the issue occurs.")
    issue: str = Field(description="A brief description of the issue.")
    severity: Literal["low", "medium", "high", "critical"] = Field(description="Severity of the issue.")

class CodeReviewAction(Action):
    comments: List[Comment] = Field(default_factory=list, description="List of comments for the code review.")
    decision: Literal["approve", "request_changes"] = Field(description="Final decision on the code snippet.")

class CodeReviewObservation(Observation):
    code_snippet: str = Field(description="The Python code snippet to review.")
    task_id: str = Field(description="The ID of the current task.")

class CodeReviewState(State):
    task_id: str
    code_snippet: str
    known_issues: List[str]
    difficulty: str