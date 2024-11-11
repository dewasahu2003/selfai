class DataFormatter:
    @classmethod
    def get_system_prompt(cls, data_type: str) -> str:
        return (
            f"I will give you batches of contents of {data_type}. Please generate me exactly 1 instruction for each of them. The {data_type} text "
            f"for which you have to generate the instructions is under Content number x lines. Please structure the answer in json format,"
            f"ready to be loaded by json.loads(), a list of objects only with fields called instruction and content. For the content field, copy the number of the content only!."
            f"Please do not add any extra characters and make sure it is a list with objects in valid json format!\n"
        )

    @classmethod
    def format_data(cls, data_points: list, is_example: bool, start_idx: int) -> str:
        text = ""
        for idx, data_point in enumerate(data_points):
            if not is_example:
                text += f"Content number {start_idx+idx}\n"
            text += str(data_point) + "\n"
        return text

    @classmethod
    def format_batch(cls, context_msg: str, data_points: list, start_idx: int) -> str:
        delimiter_msg = context_msg
        delimiter_msg += cls.format_data(data_points, False, start_idx)
        return delimiter_msg

    @classmethod
    def format_promt(cls, inference_posts: str, data_type: str, start_idx: int) -> str:
        initial_prompt = cls.get_system_prompt(data_type)
        initial_prompt += f"You must generate exactly a list of {len(inference_posts)} json objects, using the contents provided under CONTENTS FOR GENERATION\n"
        initial_prompt += cls.format_batch(
            "\nCONTENTS FOR GENERATION\n", inference_posts, start_idx
        )
        return initial_prompt
