import concurrent.futures


import utils
from db import QdrantDBConnector
from qdrant_client import models
from config import settings
from query_expansion import QueryExpansion
from reranking import ReRanker
from self_query import SelfQuery
from sentence_transformers.SentenceTransformer import SentenceTransformer
from utils.logging import get_logger

logger = get_logger(__name__)


class VectorRetriever:
    """
    getting vector embeddings from qdrant - using query expansion and multitency search
    """

    def __init__(self, query: str):
        self._client = QdrantDBConnector()
        self._query = query
        self._query_expander = QueryExpansion()
        self._reranker = ReRanker()
        self._metadata_extractor = SelfQuery()
        self._embedder = SentenceTransformer(settings.EMBEDDING_MODEL_ID)

    def _search_single_query(
        self, generated_query: str, metadata_filter_value: str | None, k: int
    ):
        """
        searching for query in db
        """
        assert k > 3, "k must be greater than 3"
        # getting embeddings
        query_vector = self._embedder.encode(generated_query).tolist()
        # searching for query in qdrant
        vectors = []
        vector_posts = self._client.search(
            collection_name="vector_posts",
            query_filter=(
                models.Filter(
                    must=[
                        models.FieldCondition(
                            key="author_id",
                            match=models.MatchValue(value=metadata_filter_value),
                        )
                    ]
                )
                if metadata_filter_value
                else None
            ),
            query_vector=query_vector,
            limit=k // 3,
        )
        vector_articles = self._client.search(
            collection_name="vector_articles",
            query_filter=(
                models.Filter(
                    must=[
                        models.FieldCondition(
                            key="author_id",
                            match=models.MatchValue(value=metadata_filter_value),
                        )
                    ]
                )
                if metadata_filter_value
                else None
            ),
            query_vector=query_vector,
            limit=k // 3,
        )
        vector_repo = self._client.search(
            collection_name="vector_repositories",
            query_filter=(
                models.Filter(
                    must=[
                        models.FieldCondition(
                            key="author_id",
                            match=models.MatchValue(value=metadata_filter_value),
                        )
                    ]
                )
                if metadata_filter_value
                else None
            ),
            query_vector=query_vector,
            limit=k // 3,
        )
        vectors.append(vector_posts)
        vectors.append(vector_articles)
        vectors.append(vector_repo)
        return utils.flatten_list(vectors)

    def set_query(self, query: str):
        self._query = query

    def retrieve_top_k(self,k:int,to_expand_to_n_queries:int)-> list:
        generated_queries = self._query_expander.generate_response(
            self._query, to_expand_to_n_queries
        )
        logger.info(f"succesfully 
                    generated queries: {len(generated_queries)}")
        
        author_id = self._metadata_extractor.generate_response(self._query)
        if author_id:
            logger.info(f"succesfully
                        extracted author_id: {author_id}")
        else:
            logger.info(f"failed to extract author_id")
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            search_tasks = [
                executor.submit(
                    self._search_single_query,
                    query,
                    author_id,
                    k)
                    for query in generated_queries
            ]
            hits = [task.result() for task in concurrent.futures.as_completed(search_tasks)]
            hits = utils.flatten(hits)
        logger.info(f"all documents retrieved",num_doc=len(hits))
        return hits
     
    def rerank(self, hits: list,keep_top_k:int) -> list[str]:
        """
        reranking hits
        """
        content_list = [hits.payload["content"] for hits in hits]
        rerank_hits = self._reranker.generate_response(
            query=self._query,
            passages=content_list,
            keep_top_k=keep_top_k,
        )
        logger.info(f"succesfully reranked hits",num_doc=len(rerank_hits))
        return rerank_hits
