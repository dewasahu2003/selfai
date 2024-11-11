from langchain_openai import OpenAI
from llm_utils.chain import GeneralChain
from llm_utils.prompt_templates import RAGEvaluationTemplate
from config import settings
from datasets import Dataset
from pandas import DataFrame
from ragas import evaluate
from ragas.embeddings import HuggingfaceEmbeddings
from ragas.metrics import (
    answer_correctness,
    answer_similarity,
    answer_relevancy,
    context_utilization,
    context_recall,
    context_entity_recall,
)


###evaluating rag system via RAGAs
# Evaluating against the following metrics
# RETRIEVAL BASED
# 1. Context Utilization - How well the context is utilized
# 2. Context Relevancy - (VDB based) measures the relevance of retrieved context
# 3. Context Recall - How well the context is recalled in the answer
# 4. Context Entity Recall - a measure of what fraction of entities are recalled from ground_truths

# END-TO-END
# 5. Answer Similarity - measures the semantic resemblance between the answer and gt answer
# 6. Answer Corectness - measures the correctness of the answer compared to gt

METRICS = [
    context_utilization,
    context_recall,
    context_entity_recall,
    answer_correctness,
    answer_similarity,
    answer_relevancy,
]


def eval_ragas(query: str, context: list[str], output: str) -> DataFrame:
    """
    method using ragas to evaluate Rag system
    """
    data_sample = {
        "question": [query],
        "answer": [output],
        "contexts": [context],
        "ground_truth": ["".join(context)],
    }
    model = OpenAI(model=settings.OPENAI_MODEL_ID, api_key=settings.OPENAI_API_KEY)

    embedd_model = HuggingfaceEmbeddings(model=settings.EMBEDDING_MODEL_ID)
    dataset = Dataset.from_dict(data_sample)
    score = evaluate(
        llm=model, embeddings=embedd_model, dataset=dataset, metrics=METRICS
    )
    return score
