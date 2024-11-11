from utils.logging import get_logger
from inference_pipeline import SelfAi

logger = get_logger(__name__)

inference_point = SelfAi()


def lambda_handler(event, context):
    # Get the JSON data from the request
    if event.get("query", 0) != 0:

        query = event["query"]

        try:
            output = inference_point.generate(
                query=query,
                enable_rag=True,
                enable_eval=True,
                enable_monitor=True,
            )

            # Log the results
            logger.info(f"Answer: {output['answer']}")
            logger.info("=" * 50)
            logger.info(f"Evaluation Result: {output['llm_eval_result']}")

            return {"statusCode": 200, "body": f"{output['answer']}"}

        except Exception as e:
            return {"statusCode": 500, "body": f"Error occured: {str(e)}"}
    else:
        return {"statusCode": 500, "body": "no query found"}
