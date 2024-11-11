from langchain_openai import OpenAI
from llm_utils.chain import GeneralChain
from llm_utils.prompt_templates import SelfQueryTemplate
from config import settings


class SelfQuery:
    @staticmethod
    def generate_response(query: str) -> str | None:
        self_query_template = SelfQueryTemplate()
        prompt = self_query_template.create_template()

        model = OpenAI(model=settings.OPENAI_MODEL_ID, temperature=0)

        chain = GeneralChain.get_chain(
            llm=model,
            prompt=prompt,
            output_key="metadata_filter_value",
        )
        response = chain.invoke({"question": query})
        result = response.gett("metadata_filter_value", "none")
        if result.lower() == "none":
            return None
        return result
