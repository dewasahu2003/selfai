from typing import List
import comet_llm
from config import settings


class PromptMonitoringManager:
    @classmethod
    def log(
        cls,
        prompt: str,
        output: str,
        prompt_template: str | None = None,
        prompt_template_variable: dict | None = None,
        metadata: dict | None = None,
    ):
        comet_llm.init()

        metadata = metadata or {}
        metadata = {"model": settings.MODEL_NAME, **metadata}

        comet_llm.log_prompt(
            workspace=settings.COMET_WORKSPACE,
            project=f"{settings.COMET_PROJECT}-monitoring",
            api_key=settings.COMET_API_KEY,
            prompt=prompt,
            prompt_template=prompt_template,
            prompt_template_variables=prompt_template_variable,
            output=output,
            metadata=metadata,
        )

    @classmethod
    def log_chain(
        cls,
        query: str,
        context: str,
        llm_gen: str,
        llm_eval_output: str,
        rag_eval_scores: dict | None = None,
        timing: dict | None = None,
    ):
        comet_llm.init(project=f"{settings.COMET_PROJECT}-monitoring")
        comet_llm.start_chain(
            inputs={"user_query": query},
            project=f"{settings.COMET_PROJECT}-monitoring",
            api_key=settings.COMET_API_KEY,
            workspace=settings.COMET_WORKSPACE,
        )

        with comet_llm.Span(
            category="Vector Retrieval",
            name="rag_retrieval_step",
            inputs={"user_query": query},
            metadata={"duration": timing.get("retrieval")},
        ) as span:
            span.set_outputs(outputs={"retrieved_context": context})

        with comet_llm.Span(
            category="LLM Generation",
            name="llm_generation_step",
            inputs={
                "user_query": query,
            },
            metadata={
                "model_used": settings.OPENAI_MODEL_ID,
                "duration": timing.get("generation"),
            },
        ) as span:
            span.set_outputs(outputs={"generation": llm_gen})

        with comet_llm.Span(
            category="Evaluation",
            name="llm_evaluation_step",
            inputs={"query": llm_gen, "user_query": query},
            metadata={
                "model_used": settings.OPENAI_MODEL_ID,
                "duration": timing.get("llm_evaluation"),
            },
        ) as span:
            span.set_outputs(outputs={"evaluation_output": llm_eval_output})

        with comet_llm.Span(
            category="Evaluation",
            name="rag_evaluation_step",
            inputs={
                "user_query": query,
                "retrieved_context": context,
                "llm_gen": llm_gen,
            },
            metadata={
                "model_used": settings.OPENAI_MODEL_ID,
                "embd_model": settings.EMBEDDING_MODEL_ID,
                "eval_framework": "RAGAS",
                "duration": timing.get("evaluation_rag"),
            },
        ) as span:
            span.set_outputs(outputs={"rag_eval_scores": rag_eval_scores})
        comet_llm.end_chain(outputs={"response": llm_gen})
