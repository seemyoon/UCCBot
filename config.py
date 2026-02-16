import os

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from pydantic import SecretStr

load_dotenv()

CRIMINAL_CODE_DOC = 'data/criminal_code_of_ukraine.pdf'
PERSIST_DIR = './chroma_db'
LAW_NAME = "Кримінальний кодекс України"
MAX_CHUNKS_TOKENS = 1000
CHUNK_OVERLAP = 50
COLLECTION_NAME = "ucc_collection"
NUMBER_OF_RESULTS_TO_RETURN = 5

EMBEDDING_MODEL = "text-embedding-3-small"  # or "text-embedding-3-large"
GPT_MODEL = "gpt-5"

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY') or ValueError("OPENAI_API_KEY is not set in environment variables.")

EMBEDDER = OpenAIEmbeddings(
    model=EMBEDDING_MODEL,
    api_key=SecretStr(OPENAI_API_KEY),
)

LEGAL_FOOTER_PROMPT_TEMPLATE = """
You are an expert in legal documents. Your task is to process the given legal footer text and extract all information into a structured JSON.
Return **ONLY JSON** (no explanations) with the following English field names, but keep all values in Ukrainian:

- text: full footer text
- act_type: type of legal act
- act_name: name of the act
- signed_by: person or authority who signed/approved
- number_and_date: number and date of the act
- edition: edition / version information
- status: current status
- permanent_link: permanent URL of the act

Text to process:
{footer_txt}

Example JSON format:
{{
  "text": "…",
  "act_type": "…",
  "act_name": "…",
  "signed_by": "…",
  "number_and_date": "…",
  "edition": "…",
  "status": "…",
  "permanent_link": "…"
}}
"""
