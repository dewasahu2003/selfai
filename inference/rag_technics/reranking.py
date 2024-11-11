from langchain_openai import OpenAI
from llm_utils.chain import GeneralChain
from llm_utils.prompt_templates import RerankingTemplate
from config import settings


class ReRanker:
    @staticmethod
    def generate_response(
        query: str, passages: list[str], keep_top_k: int
    ) -> list[str]:
        reranking_prompt_template = RerankingTemplate()
        prompt = reranking_prompt_template.create_template(keep_top_k=keep_top_k)

        model = OpenAI(model=settings.OPENAI_MODEL_ID, temperature=0)
        chain = GeneralChain.get_chain(
            llm=model,
            template=prompt,
            output_key="rerank",
        )

        stripped_passages = [
            stripped_item for item in passages if (stripped_item := item.strip())
        ]
        # making passages "p1|p2|p3|p4|p5" -> sinle string
        passages = reranking_prompt_template.seprator.join(stripped_passages)
        response = chain.invoke({"passages": passages, "question": query})

        result = response.get("rerank", "none")
        if result.lower() == "none":
            return []
        # making passages [p1, p2, p3, p4, p5] -> list of strings
        reranked_passages = result.strip().split(reranking_prompt_template.seprator)
        stripped_passages = [
            stripped_item
            for item in reranked_passages
            if (stripped_item := item.strip())
        ]
        return stripped_passages
