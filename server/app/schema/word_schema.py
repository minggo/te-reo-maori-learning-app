from pydantic import BaseModel

class WordPublic(BaseModel):
    """
    Public representation of a Māori vocabulary word for API responses.

    Fields:
    - id (str): Unique identifier of the word (MongoDB ObjectId as string)
    - maori (str): The Māori word
    - english (str): The English translation of the word
    """
    id: str
    maori: str
    english: str
    