from InstructorEmbedding import INSTRUCTOR
from sentence_transformers import SentenceTransformer

from config import settings


def embedd_text(text: str) -> list[float]:
    """
    embedd text using sentence transformer
    """
    model = SentenceTransformer(settings.EMBEDDING_MODEL_ID)
    return model.encode(text)


def embedd_repositories(text: str) -> list[float]:
    """
    embedd text using sentence transformer
    """
    model = INSTRUCTOR("hkunlp/instructor-xl")
    sentence = text
    instruction = "Represent the structure of the repository"
    return model.encode([instruction, sentence])
