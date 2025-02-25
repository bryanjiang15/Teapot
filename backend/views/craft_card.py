from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import sqlite3
from transformers import pipeline
from backend.python_model_test import generateWord
from backend.model import get_db
import backend

# Create router
router = APIRouter()

# Define request model
class WordCombineRequest(BaseModel):
    first: str
    second: str

root_path = backend.FOLDER_ROOT
generator = pipeline("text-generation", model=root_path / "backend"/"merge_word_clm-model") #perplexity: 21.27

@router.post('/api/combine-word')
async def craft_card_route(
    request: WordCombineRequest,
    db: sqlite3.Connection = Depends(get_db)
):
    cursor = db.cursor()

    #Get the card from the database
    cursor.execute("SELECT * FROM cards WHERE name = ?", (request.first,))
    card = cursor.fetchone()

    result = generateWord(request.first, request.second, generator)
    # Process the data and create a card
    return {'result': result, 'emoji': '🔥'}

# Add router to main app
backend.app.include_router(router)