from pydantic import BaseModel, Field
from typing import List

class UserLearnedWords(BaseModel):
    """
    Stores the list of word IDs that a user has learned.
    """
    user_id: str = Field(..., description="User ID", alias="_id")
    learned_ids: List[str] = Field(default_factory=list, description="List of learned word IDs")
