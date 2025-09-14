from enum import Enum
from base64 import b64encode
from typing import Optional

from pydantic import BaseModel
from openai import OpenAI
from openai.types.responses import ResponseTextConfigParam, ResponseInputMessageContentListParam
from openai.types.responses import EasyInputMessageParam, ResponseInputImageParam, ResponseInputTextParam


class FoodErrors(str, Enum):
    NO_FOOD = "No food found"


class FoodCalories(BaseModel):
    name: str
    description: str
    total_calories: int
    error: Optional[FoodErrors]


class CalorieCounter:
    b64_image_prefix = "data:image/jpeg;base64,"

    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    @staticmethod
    def encode_image(image_bytes: bytes):
        return b64encode(image_bytes).decode("utf-8")

    def identify_calories(self, image_bytes: bytes = None, image_url: str = None, help_text: str = None) -> FoodCalories:
        if image_url is None == image_bytes is None:
            raise ValueError("Either image_url or image_bytes must be provided")

        if image_bytes is not None:
            image = self.b64_image_prefix + self.encode_image(image_bytes)

        if image_url is not None:
            image = image_url

        user_content: ResponseInputMessageContentListParam
        user_content = [ResponseInputImageParam(image_url=image, type="input_image", detail="auto")]

        help_instruction = ""
        if help_text is not None:
            help_instruction = "User provided some text information to help identify food items."
            user_content.append(ResponseInputTextParam(text=help_text, type="input_text"))

        response = self.client.responses.parse(
            model="gpt-5-mini",
            store=False,
            text=ResponseTextConfigParam(
                verbosity="low"
            ),
            text_format=FoodCalories,
            instructions=" ".join([
                "You need to identify calories in the image.",
                "List food items you see along with assumed quantities and estimated calories.",
                "Never use cups and oz.",
                "Report the total calories.",
                help_instruction
            ]),
            input=[
                EasyInputMessageParam(
                    role="user",
                    content=user_content
                )
            ]
        )

        return response.output_parsed

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    load_dotenv()

    calorie_counter = CalorieCounter(
        api_key=os.getenv("OPENAI_API_KEY")
    )

    url = ""
    calories = calorie_counter.identify_calories(image_url=url)
    print(calories)
