from langchain_openai import OpenAI
from llm_utils.chain import GeneralChain
from llm_utils.prompt_templates import LLMEvaluationTemplate
from config import settings


def evaluate_llm(query: str, output: str) -> str:
    evaluation_template = LLMEvaluationTemplate()
    evaluate_prompt = evaluation_template.create_template()

    model = OpenAI(model=settings.OPENAI_MODEL_ID, api_key=settings.OPENAI_API_KEY)
    chain = GeneralChain.get_chain(model, evaluate_prompt, output_key="evaluation")
    response = chain.invoke({"query": query, "output": output})
    return response["evaluation"]
