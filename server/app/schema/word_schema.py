from pydantic import BaseModel

class WordPublic(BaseModel):
    id: str
    maori: str
    english: str