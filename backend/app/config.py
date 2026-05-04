from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Neo4j Configuration
    neo4j_uri: str = "bolt://neo4j:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"

    # Gemini API
    gemini_api_key: str = ""

    # Data directories
    data_dir: Path = Path("./data")
    images_dir: Path = Path("./data/images")
    cache_dir: Path = Path("./cache")

    # Embedding cache
    embedding_cache_dir: Path = Path("./cache/embeddings")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()