"""UserAction signal model. Data only; does not control UI."""

from typing import Literal, Optional

from pydantic import BaseModel

ActionType = Literal[
    "TASK_COMPLETE", "ERROR", "PAGE_VIEW", "REQUEST_HELP", "PAUSE", "RESUME"
]


class UserAction(BaseModel):
    user_id: str
    action_type: ActionType
    page_id: Optional[str] = None
    detail: Optional[str] = None
