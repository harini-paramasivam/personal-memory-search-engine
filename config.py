import os

# Application settings
APP_NAME = "Personal Memory Search Engine"
APP_VERSION = "1.0"

# Directory paths
DATA_DIR = "data"
DOCUMENTS_DIR = os.path.join(DATA_DIR, "documents")
IMAGES_DIR = os.path.join(DATA_DIR, "images")
AUDIO_DIR = os.path.join(DATA_DIR, "audio")
EMBEDDINGS_DIR = os.path.join(DATA_DIR, "embeddings")
DATABASE_PATH = os.path.join(DATA_DIR, "database.sqlite")

# Ensure directories exist
for directory in [DATA_DIR, DOCUMENTS_DIR, IMAGES_DIR, AUDIO_DIR, EMBEDDINGS_DIR]:
    os.makedirs(directory, exist_ok=True)

# Search settings
DEFAULT_SEARCH_RESULTS = 10
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Can be changed to other models

# UI settings
THEME_COLOR = "#3E7CB9"
SECONDARY_COLOR = "#FF924C"