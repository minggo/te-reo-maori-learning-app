# app/schema/mistake_schema.py

from pydantic import BaseModel, Field
from typing import List, Optional

class MistakeSubmission(BaseModel):
    """
    Schema for submitting a list of wrong word IDs from a user after a quiz.

    Fields:
    - user_id (str): User identifier or session ID. Default is 'anonymous'.
    - wrong_word_ids (List[str]): List of word ObjectId (as string) the user answered incorrectly in this quiz.
    """
    user_id: Optional[str] = Field(default="anonymous", description="User identifier or session ID")
    wrong_word_ids: List[str] = Field(..., description="List of word _id values the user answered incorrectly")

class QuizItem(BaseModel):
    """
    Schema for quiz word returned to the client, with an indicator if it is a review (previous mistake) word.

    Fields:
    - id (str): MongoDB ObjectId as string.
    - maori (str): Māori word.
    - options List[str]: List of possible answer choices for this quiz item. The correct answer is included in this list.
    - answer (str): The correct answer for this word.
    - is_review (bool): True if this word was previously answered incorrectly by the user (i.e., is a review word).
    """
    id: str
    maori: str
    options: List[str]
    answer: str
    is_review: bool = False
