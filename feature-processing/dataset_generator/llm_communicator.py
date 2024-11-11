import json
from openai import OpenAI
from config import settings
from utils.logging import get_logger

MAX_LEN = 16384
SYSTEM_PROMPT = (
    "You are a technical writer handling someone's account to post about AI and MLOPS"
)

logger = get_logger(__name__)


class GPTCommunicator:
    """
    connecting with gpt
    """

    def __init__(self, gpt_model: str = "gpt-3.5-turbo"):
        self.api_key = settings.OPENAI_API_KEY
        self.gpt_model = gpt_model or settings.OPENAI_MODEL_ID

    def send_prompt(self, promt: str) -> list:
        try:
            client = OpenAI(api_key=self.api_key)
            logger.info(f"Sending prompt to gpt: {promt}")

            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": promt[:MAX_LEN]},
                ],
                model=self.gpt_model,
            )
            response = chat_completion.choices[0].message.content
            return json.loads(self.clean_response(response))
        except Exception:
            logger.exception("Error while sending prompt to gpt")
            return []

    @staticmethod
    def clean_response(self, response: str) -> str:
        """
        cleaning response from gpt
        """
        start_idx = response.find("[")
        end_idx = response.rfind("]")
        return response[start_idx : end_idx + 1]
