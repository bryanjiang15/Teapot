from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pathlib

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

FOLDER_ROOT = pathlib.Path(__file__).resolve().parent.parent
DATABASE_FILENAME = FOLDER_ROOT / "var" / "cards.db"

# Import views after app initialization
import backend.views