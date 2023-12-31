from enum import IntEnum


class UserContant(IntEnum):
    MAX_USER_EMAIL_LENGTH = 30
    MAX_USERNAME_LENGTH = 40
    MAX_USER_NAME_LENGTH = 50


class FoodContant(IntEnum):
    MAX_TAG_NAME_LENGTH = 20
    MAX_MEASUREMENT_UNIT_LENGTH = 10
    MAX_RECIPE_NAME_LENGHT = 50
    MIN_AMOUNT = 0
    MIN_COOKING_TIME = 1
    MAX_COOKING_TIME = 10000
    MAX_INGREDIENT_NAME = 200
    PAGE_SIZE = 6
