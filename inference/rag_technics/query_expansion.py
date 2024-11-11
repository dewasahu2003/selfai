from langchain_openai import ChatOpenAI

from llm_utils.chain import GeneralChain
from llm_utils.prompt_templates import QueryExpansionTemplate
from config import settings


class QueryExpansion:
    @staticmethod
    def generate_response(query: str, to_expand_to_n: int = 5) -> list[str]:
        query_expansion_template = QueryExpansionTemplate()
        prompt_template = query_expansion_template.create_template(to_expand_to_n)

        model = ChatOpenAI(temperature=0, model=settings.OPENAI_MODEL_ID)
        chain = GeneralChain.get_chain(
            llm=model, template=prompt_template, output_key="expanded_queries"
        )

        response = chain.invoke({"question": query})
        result = response["expanded_queries"]

        queries = result.strip().split(query_expansion_template.seprator)
        stripped_queries = [
            stripped_item for item in queries if (stripped_item := item.strip())
        ]
        return stripped_queries
