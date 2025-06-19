import random
from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime, timezone
from bson import ObjectId
from app.db.mongodb import db
from app.schema.mistake_schema import MistakeSubmission, QuizItem
from app.constants import (
    COLLECTION_NAME,
    COLLECTION_USER_MISTAKES,
    COLLECTION_QUIZ_HISTORY
)

router = APIRouter()

async def get_total_words():
    """
    Get the total number of words in the collection.
    """
    return await db[COLLECTION_NAME].estimated_document_count({})

async def get_sorted_user_mistakes(user_id):
    """
    Fetch and sort the user's mistake words by count and last_wrong date.
    Returns a list of word dicts sorted by (-count, -last_wrong).
    """
    mistake_doc = await db[COLLECTION_USER_MISTAKES].find_one({"_id": user_id})
    mistakes = mistake_doc.get("wrong_words", []) if mistake_doc else []
    mistakes = sorted(
        mistakes,
        key=lambda m: (-m.get("count", 0), -(m.get("last_wrong") or datetime.min).timestamp())
    )
    return mistakes

async def get_candidate_ids(wrong_ids, limit):
    """
    Select candidate quiz word IDs: prioritize wrong_ids, fill up with random if needed.
    """
    candidate_ids = wrong_ids[:]
    if len(candidate_ids) < limit:
        all_ids = [str(word["_id"]) async for word in db[COLLECTION_NAME].find({}, {"_id": 1})]
        rest_ids = [id for id in all_ids if id not in candidate_ids]
        random.shuffle(rest_ids)
        candidate_ids.extend(rest_ids[:limit - len(candidate_ids)])
    return candidate_ids[:limit]

async def get_id2word(candidate_ids):
    """
    Get a mapping from word ID to word document for the quiz questions.
    """
    id2_word = {}
    cursor = db[COLLECTION_NAME].find({"_id": {"$in": [ObjectId(id) for id in candidate_ids]}})
    async for word in cursor:
        id2_word[str(word["_id"])] = word
    return id2_word

async def get_all_english_words():
    """
    Get all English translations in the collection (for distractors).
    """
    all_words = [w async for w in db[COLLECTION_NAME].find({}, {"_id": 1, "english": 1})]
    return [w["english"] for w in all_words]

def make_quiz_question(qid, word, all_english, is_review):
    """
    Create a single QuizItem (with correct answer and 3 random distractors).
    """
    correct = word["english"]
    options = set([correct])
    distractors = random.sample(
        [eng for eng in all_english if eng != correct],
        min(3, len(all_english) - 1)
    )
    options.update(distractors)
    options = list(options)
    random.shuffle(options)
    return QuizItem(
        id=qid,
        maori=word["maori"],
        options=options,
        answer=correct,
        is_review=is_review
    )

@router.get("/quiz", response_model=List[QuizItem])
async def get_quiz(user_id: str = "anonymous", limit: int = 10):
    """
    Get a quiz with multiple-choice questions (4 options per Māori word).

    - For each question, the Māori word is given along with 4 English options (one correct).
    - User's previous mistake words are prioritized for selection,
      and are sorted first by highest wrong count, then by most recent mistake date (descending).
    - If there are not enough mistake words, random words are used to fill up the remaining questions.
    """
    total_words = await get_total_words()
    if total_words == 0:
        raise HTTPException(status_code=404, detail="No words available for quiz")

    limit = max(1, min(limit, total_words))  # Clamp limit to [1, total_words]
    mistakes = await get_sorted_user_mistakes(user_id)
    wrong_ids = [m["id"] for m in mistakes]

    candidate_ids = await get_candidate_ids(wrong_ids, limit)
    id2_word = await get_id2word(candidate_ids)
    all_english = await get_all_english_words()

    quiz_questions = []
    for qid in candidate_ids:
        word = id2_word.get(qid)
        if not word:
            continue
        quiz_questions.append(
            make_quiz_question(qid, word, all_english, is_review=(qid in wrong_ids))
        )
    return quiz_questions
    
async def filter_valid_word_ids(db, word_ids):
    existing = await db[COLLECTION_NAME].find(
        {"_id": {"$in": word_ids}},
        {"_id": 1}
    ).to_list(None)
    return [doc["_id"] for doc in existing]

async def update_mistake_records(db, user_id, valid_word_ids, now):
    for word_id in valid_word_ids:
        result = await db[COLLECTION_USER_MISTAKES].update_one(
            {"_id": user_id, "wrong_words.id": word_id},
            {
                "$inc": {"wrong_words.$.count": 1},
                "$set": {"wrong_words.$.last_wrong": now}
            },
            upsert=False
        )
        if result.matched_count == 0:
            await db[COLLECTION_USER_MISTAKES].update_one(
                {"_id": user_id},
                {
                    "$push": {
                        "wrong_words": {
                            "id": word_id,
                            "count": 1,
                            "last_wrong": now
                        }
                    }
                },
                upsert=True
            )

async def save_quiz_history(db, user_id, valid_word_ids, now):
    if valid_word_ids:
        await db[COLLECTION_QUIZ_HISTORY].insert_one({
            "user_id": user_id,
            "wrong_word_ids": valid_word_ids,
            "timestamp": now
        })


@router.post("/quiz_result")
async def submit_quiz_result(submission: MistakeSubmission):
    """
    Record the user's quiz mistakes and update their mistake log.

    - For each wrong word, increment the mistake count or add a new entry.
    - Save the current quiz result to the history collection.

    Args:
        submission (MistakeSubmission): Contains user_id and wrong_word_ids.

    Returns:
        dict: Confirmation message and number of wrong words.
    """
    now = datetime.now(timezone.utc)
    user_id = submission.user_id or "anonymous"
    wrong_word_ids = submission.wrong_word_ids or []

    
    valid_word_ids = await filter_valid_word_ids(db, wrong_word_ids)

    await update_mistake_records(db, user_id, valid_word_ids, now)
    await save_quiz_history(db, user_id, valid_word_ids, now)

    return {"message": "Quiz result recorded.", "wrong_count": len(wrong_word_ids)}