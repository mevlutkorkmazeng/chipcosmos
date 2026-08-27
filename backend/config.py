"""Backend genelinde kullanılan sabitler ve ayarlar."""

from pathlib import Path

BACKEND_DIR = Path(__file__).parent
PROJECT_DIR = BACKEND_DIR.parent

DB_PATH = str(PROJECT_DIR / "rag.db")
UPLOAD_DIR = PROJECT_DIR / "data" / "uploads"

EMBEDDING_MODEL_ALIAS = "qwen3-embedding-0.6b"
CHAT_MODEL_ALIAS = "phi-3.5-mini"
CHAT_MAX_TOKENS = 180

# get_top_chunks()'ın en iyi skoru bu eşiğin altındaysa, retrieval'in konuyla
# gerçekten ilgili bir pasaj bulamadığını varsayıp cevaba bir uyarı ekleriz.
CONFIDENCE_THRESHOLD = 0.35
LOW_CONFIDENCE_NOTE = (
    "\n\nNot: Bu konuda dokümanlarımda net bir bilgi bulamadım, en yakın "
    "bulduğum bilgiyi paylaşıyorum ama emin değilim."
)

TOPICS = ["Semiconductors", "Space Exploration"]

ALLOWED_EXTENSIONS = {".txt", ".md", ".pdf", ".docx"}
MAX_UPLOAD_MB = 50

SYSTEM_PROMPT_TEMPLATE = (
    "You must answer using ONLY the information in the context below. "
    "If the answer is not explicitly stated in the context, respond with "
    'EXACTLY this and nothing else: "I don\'t know based on the provided '
    "documents.\" Do not use any outside knowledge, even if you know the "
    "answer. When citing context, refer to it by its topic/title only "
    '(e.g. "According to the passage on MOSFETs..."), NEVER by a number '
    'like "passage 1".'
    "\n\nContext:\n{context}"
)
