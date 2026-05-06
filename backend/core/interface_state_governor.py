"""
Noni - Interface State Governor.
Backend-governed progression control.
All user state transitions are managed here.
"""
from enum import Enum
from typing import Optional
from pydantic import BaseModel


class UserState(str, Enum):
    """User progression states."""
    ONBOARDING = "onboarding"
    ACTIVE = "active"
    PAUSED = "paused"
    REVIEW = "review"


class StateTransition(BaseModel):
    """State transition request/record."""
    user_id: str
    from_state: UserState
    to_state: UserState
    reason: Optional[str] = None
    approved_by: Optional[str] = None


class InterfaceStateGovernor:
    """
    Backend authority for all user state management.
    
    RULES:
    - All progression decisions live in backend code
    - The frontend NEVER determines user state
    - All user advancement is reversible
    - No automated actions without explicit review
    """
    
    def __init__(self):
        self._state_registry: dict[str, UserState] = {}
    
    def get_user_state(self, user_id: str) -> UserState:
        """Retrieve current state for a user."""
        return self._state_registry.get(user_id, UserState.ONBOARDING)
    
    def request_transition(
        self, 
        user_id: str, 
        to_state: UserState, 
        reason: Optional[str] = None
    ) -> StateTransition:
        """Request a state transition (requires backend approval)."""
        current_state = self.get_user_state(user_id)
        
        transition = StateTransition(
            user_id=user_id,
            from_state=current_state,
            to_state=to_state,
            reason=reason
        )
        
        # Transition logic here - all decisions backend-controlled
        return transition
