import json
from comet_ml import Experiment, Artifact
from utils.logging import get_logger
from db import QdrantDBConnector
from llm_communicator import GPTCommunicator
from data_formatter import DataFormatter
from config import settings

logger = get_logger(__name__)

_client = QdrantDBConnector()


class DatasetGenerator:
    def __init__(
        self, api_communicator: GPTCommunicator, data_formatter: DataFormatter
    ):
        self.api_communicator = api_communicator
        self.data_formatter = data_formatter

    def generate_training_data(
        self, collection_name: str, data_type: str, batch_size: int = 1
    ):
        all_content = self.fetch_all_cleaned_content(collection_name)
        response = []
        for i in range(0, len(all_content), batch_size):
            batch = all_content[i : i + batch_size]
            prompt = self.data_formatter.format_promt(batch, data_type, i)
            response += self.api_communicator.send_prompt(prompt)

            for jdx in range(i, i + batch_size):
                response[jdx]["content"] = all_content[jdx]

        self.push_to_comet(response, data_type, collection_name)

    def push_to_comet(self, data: list, data_type: str, collection_name: str):
        try:
            logger.info(f"Pushing data to Comet for {collection_name}...")

            experiment = Experiment(
                api_key=settings.COMET_API_KEY,
                project_name=settings.COMET_PROJECT,
                workspace=settings.COMET_WORKSPACE,
            )

            file_name = f"{collection_name}.json"
            logger.info(f"Saving data to {file_name}...")

            artifact = Artifact(file_name=file_name)
            with open(file_name, "w") as f:
                json.dump(data, f)
            logger.info(f"Saved data to {file_name}...")

            artifact = Artifact(f"{data_type}-instruct-dataset")
            artifact.add(file_name)
            logger.info(f"Adding artifact to Comet...")

            experiment.log_artifact(artifact)
            experiment.end()
            logger.info(f"Data pushed to Comet and experiment ended.")

        except Exception as e:
            logger.error(f"Error pushing data to Comet: {e}", exc_info=True)

    def fetch_all_cleaned_content(self, collection_name: str):
        all_cleaned_contents = []

        # getting data step by step not at once
        scroll_response = _client.scroll(collection_name=collection_name, limit=1000)
        # getting payload lists as 0th element
        points = scroll_response[0]

        for point in points:
            cleaned_content = point.payload["cleaned_content"]
            if cleaned_content:
                all_cleaned_contents.append(cleaned_content)
        return all_cleaned_contents


if __name__ == "__main__":

    def lambda_handler(event, context):
        if event["run_dataset_generation"] == "true":
            try:

                api_communicator = GPTCommunicator()
                data_formatter = DataFormatter()
                dataset_generator = DatasetGenerator(api_communicator, data_formatter)

                collections = [
                    ("cleaned_articles", "article"),
                    ("cleaned_posts", "posts"),
                    ("cleaned_repositories", "repositories"),
                ]

                for collection_name, data_type in collections:
                    logger.info(
                        f"Generating training data for",
                        collection_name=collection_name,
                        data_type=data_type,
                    )
                    dataset_generator.generate_training_data(
                        collection_name, data_type, batch_size=1
                    )
                return {
                    "statusCode": 200,
                    "body": "Data Generated processed Succesfully",
                }
            except Exception as e:
                return {"statusCode": 500, "body": f"Error occured: {str(e)}"}
        else:
            return {"statusCode": 500, "body": f"Not found"}
