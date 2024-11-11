from .utils import get_logger   
import os

import pandas as pd
import qwak
import torch as th
import yaml
from comet_ml import Experiment
from datasets import Dataset, load_dataset, DatasetDict

from peft import LoraConfig, PeftModel, get_peft_model, prepare_model_for_kbit_training

# for model configuration
from qwak.model.adapters import DefaultOutputAdapter
from qwak.model.base import QwakModel
from qwak.model.schema import ModelSchema
from qwak.model.schema_entities import InferenceOutput, RequestInput

from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    PreTrainedModel,
    Trainer,
    TrainingArguments,
)

from dataset_client import DatasetClient
from config import settings

import structlog

logger = get_logger(__name__)


class MixtralModel(QwakModel):
    """
    A Mixtral class for fine-tuning a language model.
    """

    def __init__(
        self,
        is_saved: bool = False,
        model_save_dir: str = "./model",
        model_name: str = "mistralai/Mistral-7B-Instruct-v0.1",
        comet_artifact_name: str = "posts-instruct-dataset",
        config_file: str = "./training_config.yaml",
    ):
        self._prep_environment()
        self.experiment: Experiment = None
        self.model_save_dir = model_save_dir
        self.model_name = model_name
        self.comet_dataset_artifact = comet_artifact_name
        self.training_args_config_file = config_file
        if is_saved:
            self.experiment = Experiment(
                api_key=settings.COMET_API_KEY,
                project_name=settings.COMET_PROJECT_NAME,
                workspace=settings.COMET_WORKSPACE,
            )

    def _prep_environment(self):
        """
        Prepares the environment for fine-tuning.
        """
        os.environ["TOKENIZERS_PARALLELISM"] = settings.TOKENIZER_PARALLELISM
        th.cuda.empty_cache()
        logger.info("Emptied cuda cache, ENVIRONMENT READY")

    def _init_4bit_config(self) -> None:
        """
        Initialize the 4-bit configuration for the model.
        """
        self.nf4_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=th.bfloat16,  # bfloat16 holds good range of value doesnt round stuff,but float16 would round 10^-20 to 0
        )
        if self.experiment:
            self.experiment.log_parameters(self.nf4_config)
        logger.info("Initialised config for 4-bit configuration")

    def init_model(self) -> None:
        """
        Initialize the model.
        """
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            token=settings.HUGGINGFACE_ACCESS_TOKEN,
            device_map=th.cuda.current_device(),
            quantization_config=self.nf4_config,
            use_cache=False,
            torchscript=True,
        )
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            token=settings.HUGGINGFACE_ACCESS_TOKEN,
        )
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.tokenizer.padding_side = "right"
        logger.info(f"Initialised model {self.model_name} Successfully")

    def _initialize_qlora(self, model: PreTrainedModel) -> PeftModel:
        """ "
        Initialize the model for QLoRA training.
        """
        self.qlora_config = LoraConfig(
            lora_alpha=16,  # influence on model weights | range 8-32
            lora_dropout=0.1,  # avoid overfitting | range 0-0.3
            r=64,  # rank or how much model can learn and store | range 16-128
            bias="none",  # influence model behavoir | "none" or "all" or "lora"
            task_type="CAUSAL_LM",
        )
        if self.experiment:
            self.experiment.log_parameters(self.qlora_config)

        model = prepare_model_for_kbit_training(model)
        model = get_peft_model(model, self.qlora_config)
        logger.info("Initialised QLoRA config")
        return model

    def _init_training_args(self) -> None:
        with open(self.training_args_config_file, "r") as file:
            config = yaml.safe_load(file)
        self.training_arguments = TrainingArguments(**config["training_arguments"])
        if self.experiment:
            self.experiment.log_parameters(self.training_arguments)
            logger.info("Initialised training arguments")

    def tokenize(self, prompt: str) -> dict:
        """
        Tokenize the prompt.
        """
        result = self.tokenizer(
            prompt, padding="max_length", max_length=1024, truncation=True
        )
        result["labels"] = result["input_ids"].copy()
        return result

    def generate_prompt(self, sample: dict) -> dict:
        full_prompt = (
            f"""<s>[INST]{sample["instruction"]}[/INST] {sample["content"]}</s>"""
        )
        result = self.tokenize(full_prompt)
        return result

    def preprocess_data_split(self, raw_datasets: DatasetDict) -> DatasetDict:
        """
        Preprocess the dataset.
        """
        train_data = raw_datasets["train"]
        test_data = raw_datasets["test"]
        generated_train_dataset = train_data.map(self.generate_prompt)
        generated_train_dataset = generated_train_dataset.remove_columns(
            ["instruction", "content"]
        )

        generated_test_dataset = test_data.map(self.generate_prompt)
        generated_test_dataset = generated_test_dataset.remove_columns(
            ["instruction", "content"]
        )
        return generated_train_dataset, generated_test_dataset

    def load_dataset(
        self,
    ) -> DatasetDict:
        """
        Load the dataset.
        """
        dataset_handler = DatasetClient()
        train_data_file, test_data_file = dataset_handler.download_dataset(
            file_name=self.comet_dataset_artifact
        )

        data_file = {"train": train_data_file, "test": test_data_file}
        raw_datasets = load_dataset("json", data_files=data_file)

        train_dataset, test_dataset = self.preprocess_data_split(
            raw_datasets=raw_datasets
        )
        return DatasetDict(
            {
                "train": train_dataset,
                "test": test_dataset,
            }
        )

    def _remove_model_class_attributes(self) -> None:
        """
        # Remove class attributes to skip default serialization with Pickle done by Qwak
        """
        del self.model
        del self.trainer
        del self.experiment

    def build(self):
        """
        Build the model.
        """
        self._init_4bit_config()
        self.init_model()
        if self.experiment:
            self.experiment.log_parameter(self.nf4_config)
        self.model = self._initialize_qlora(self.model)
        self._init_training_args()

        tokenised_dataset = self.load_dataset()
        self.device = th.device("cuda" if th.cuda.is_available() else "cpu")
        self.model = self.model.to(self.device)

        self.trainer = Trainer(
            model=self.model,
            args=self.training_arguments,
            train_dataset=tokenised_dataset["train"],
            eval_dataset=tokenised_dataset["test"],
            tokenizer=self.tokenizer,
        )
        logger.info("Initialised trainer")
        self.trainer.train()
        logger.info("Training completed")
        self.trainer.save_model(self.model_save_dir)
        logger.info(f"Model saved to {self.model_save_dir}")
        self.experiment.end()
        self._remove_model_class_attributes()

    def schema(self) -> ModelSchema:
        return ModelSchema(
            inputs=[RequestInput(name="instruction", type=str)],
            outputs=[InferenceOutput(name="content", type=str)],
        )

    @qwak.api(output_adapter=DefaultOutputAdapter())
    def predict(self, df):
        input_text = list(df["instruction"].values)
        input_ids = self.tokenizer(
            input_text, return_tensors="pt", add_special_tokens=True
        )
        input_ids = input_ids.to(self.device)

        generated_ids = self.model.generate(
            **input_ids,
            max_new_tokens=500,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id,
        )
        decoded_output = self.tokenizer.batch_decode(
            generated_ids[input_ids.shape[0] : 1]
        )[0]

        return pd.DataFrame(
            {"content": [decoded_output]},
        )
