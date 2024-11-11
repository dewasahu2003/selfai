from .utils import get_logger
import os
import json

from comet_ml import Experiment
from config import settings
from sklearn.model_selection import train_test_split

logger = get_logger(__name__)


class DatasetClient:
    """
    A client for interacting with the dataset. in cometml
    """

    def __init__(self, output_dir: str = "./artifacts"):
        self.output_dir = output_dir
        self.project = settings.COMET_PROJECT_NAME
        self.api_key = settings.COMET_API_KEY
        self.experiment = Experiment(api_key=self.api_key, project_name=self.project)

    def get_artifact(self, artifact_name: str):
        """
        Get the artifact from the cometml
        """
        try:
            logged_artifact = self.experiment.get_artifact(artifact_name=artifact_name)
            logged_artifact.download(output_dir=self.output_dir)
            self.experiment.end()

            logger.info(
                f"Artifact {artifact_name} downloaded successfully.at {self.output_dir}"
            )
        except Exception as e:
            logger.error(f"Error downloading artifact {artifact_name}: {str(e)}")

    def split_data(self, artifact_name: str) -> tuple:
        """
        Split the data into train and test sets.
        """
        try:
            training_file_path = os.path.join(self.output_dir, "train.json")
            test_file_path = os.path.join(self.output_dir, "test.json")

            file_name = artifact_name + ".json"

            with open(os.path.join(self.output_dir, file_name), "r") as file:
                data = json.load(file)

            train_data, test_data = train_test_split(
                data, test_size=0.2, random_state=42
            )

            with open(training_file_path, "w") as train_file:
                json.dump(train_data, train_file)

            with open(test_file_path, "w") as test_file:
                json.dump(test_data, test_file)
            logger.info(
                f"Data split successfully. Train data saved to {training_file_path}, Test data saved to {test_file_path}"
            )

            return training_file_path, test_file_path

        except Exception as e:
            logger.error(f"Error splitting data: {str(e)}")

    def download_dataset(self, file_name: str):
        self.get_artifact(artifact_name=file_name)
        return self.split_data(artifact_name=file_name)
