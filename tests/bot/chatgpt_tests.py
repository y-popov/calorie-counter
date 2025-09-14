import pytest

from bot.chatgpt import identify_calories, FoodErrors

@pytest.fixture(scope="session")
def food_image_url() -> str:
    return "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Shoyu_ramen%2C_at_Kasukabe_Station_%282014.05.05%29_1.jpg/960px-Shoyu_ramen%2C_at_Kasukabe_Station_%282014.05.05%29_1.jpg"

@pytest.fixture(scope="session")
def not_food_image_url() -> str:
    return "https://upload.wikimedia.org/wikipedia/commons/thumb/6/68/Orange_tabby_cat_sitting_on_fallen_leaves-Hisashi-01A.jpg/500px-Orange_tabby_cat_sitting_on_fallen_leaves-Hisashi-01A.jpg"

def test_identify_calories(food_image_url) -> None:
    calories = identify_calories(image_url=food_image_url)
    assert calories.total_calories > 0
    assert "ramen" in calories.name.lower()

def test_identify_calories_not_food(not_food_image_url) -> None:
    calories = identify_calories(image_url=not_food_image_url)
    assert calories.error == FoodErrors.NO_FOOD
    assert calories.total_calories == 0
