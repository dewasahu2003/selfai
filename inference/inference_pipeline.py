import time
import pandas as pd
from evaluation.model_eval import evaluate_llm
from evaluation.rag_eval import eval_ragas
from llm_utils.prompt_templates import InferenceTemplate
from monitoring.monitor import PromptMonitoringManager
from qwak_inference import RealTimeClient
from rag_technics.retriever import VectorRetriever
from config import settings


class SelfAi:
    def __init__(self):
        self.qwak_client = RealTimeClient(
            model_id=settings.QWAK_DEPLOYMENT_MODEL_ID,
        )
        self.inference_template = InferenceTemplate()
        self.prompt_monitoring_manager = PromptMonitoringManager()
        self._timing = {
            "retrieval": 0,
            "generation": 0,
            "llm_evaluation": 0,
            "evaluation_rag": 0,
        }

    def generate(
        self,
        query: str,
        enable_rag: bool = False,
        enable_eval: bool = False,
        enable_monitor: bool = True,
    ) -> dict:
        inference_prompt_template = self.inference_template.create_template(
            enable_rag=enable_rag
        )
        inference_prompt_variable = {"question": query}

        # if rag is enabled, we need to retrieve the context from the vector database
        if enable_rag:
            start_time = time.time_ns()
            retriever = VectorRetriever(query=query)
            hits = retriever.retrieve_top_k(
                k=settings.TOP_K_RETRIEVAL,
                to_expand_to_n_queries=settings.EXPAND_N_QUERY,
            )

            context = retriever.rerank(hits=hits, keep_top_k=settings.KEEP_TOP_K)

            inference_prompt_variable["context"] = context
            prompt = inference_prompt_template.format(question=query, context=context)
            end_time = time.time_ns()
            self._timing["retrieval"] += (end_time - start_time) / 1e9
        else:
            prompt = inference_prompt_template.format(question=query)

        start_time = time.time_ns()
        input_ = pd.DataFrame([{"instruction": prompt}]).to_json()

        response: list[dict] = self.qwak_client.predict(input_=input_)
        answer = response[0]["content"]
        end_time = time.time_ns()
        self._timing["generation"] += (end_time - start_time) / 1e9

        # if eval is enabled, we need to evaluate the llm output
        if enable_eval:
            if enable_rag:
                start_time = time.time_ns()
                rag_eval_score = eval_ragas(query=query, context=context, output=answer)
                end_time = time.time_ns()
                self._timing["evaluation_rag"] += (end_time - start_time) / 1e9

            start_time = time.time_ns()
            llm_eval = evaluate_llm(query=query, output=answer)
            end_time = time.time_ns()
            self._timing["llm_evaluation"] += (end_time - start_time) / 1e9
            eval_results = {
                "llm_eval": "" if not llm_eval else llm_eval,
                "rag_eval": {} if not rag_eval_score else rag_eval_score,
            }
        else:
            eval_results = None

        # if monitor is enabled, we need to log the prompt and output to comet
        if enable_monitor:
            self.prompt_monitoring_manager.log(
                prompt=prompt,
                output=answer,
                prompt_template=inference_prompt_template.template,
                prompt_template_variable=inference_prompt_variable,
            )

            self.prompt_monitoring_manager.log_chain(
                query=query,
                context=context,
                llm_gen=answer,
                llm_eval_output=eval_results["llm_eval"] if enable_eval else None,
                rag_eval_scores=eval_results["rag_eval"] if enable_eval else None,
                timing=self._timing,
            )

        return {"answer": answer, "llm_eval_result": eval_results}
