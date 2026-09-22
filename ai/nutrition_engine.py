import os
import re
import pandas as pd


class NutritionEngine:
    """
    DiaMind AI Nutrition Recommendation Engine

    Reads:
        data/diet.csv

    Expected columns:
        Condition
        Include
        Avoid
    """

    def __init__(self, csv_path="data/diet.csv"):
        self.csv_path = csv_path
        self.data = self._load_dataset()

    # =========================================================
    # LOAD DATASET
    # =========================================================

    def _load_dataset(self):

        if not os.path.exists(self.csv_path):
            print(
                f"[NutritionEngine] Dataset not found: "
                f"{self.csv_path}"
            )

            return pd.DataFrame(
                columns=[
                    "Condition",
                    "Include",
                    "Avoid"
                ]
            )

        try:

            df = pd.read_csv(
                self.csv_path
            )

            df.columns = [
                str(column).strip()
                for column in df.columns
            ]

            required = {
                "Condition",
                "Include",
                "Avoid"
            }

            missing = required - set(df.columns)

            if missing:

                print(
                    "[NutritionEngine] Missing columns:",
                    missing
                )

                return pd.DataFrame(
                    columns=list(required)
                )

            df = df.fillna("")

            return df

        except Exception as error:

            print(
                "[NutritionEngine] CSV error:",
                error
            )

            return pd.DataFrame(
                columns=[
                    "Condition",
                    "Include",
                    "Avoid"
                ]
            )

    # =========================================================
    # NORMALIZE CONDITION
    # =========================================================

    def normalize_condition(
        self,
        diabetes_type=None
    ):

        if not diabetes_type:
            return "general"

        value = str(
            diabetes_type
        ).lower().strip()

        if "type 1" in value:
            return "type 1"

        if "type 2" in value:
            return "type 2"

        if "prediabetes" in value:
            return "prediabetes"

        if "diabetes" in value:
            return "diabetes"

        return "general"

    # =========================================================
    # FIND DATASET ROW
    # =========================================================

    def get_condition_data(
        self,
        diabetes_type=None
    ):

        condition = self.normalize_condition(
            diabetes_type
        )

        if self.data.empty:

            return {
                "condition": condition,
                "include": [],
                "avoid": []
            }

        conditions = (
            self.data["Condition"]
            .astype(str)
            .str.lower()
            .str.strip()
        )

        # Exact/partial condition matching
        matches = self.data[
            conditions.str.contains(
                re.escape(condition),
                na=False
            )
        ]

        # Try diabetes if exact type isn't present
        if matches.empty:

            matches = self.data[
                conditions.str.contains(
                    "diabetes",
                    na=False
                )
            ]

        include = []
        avoid = []

        for _, row in matches.iterrows():

            include.extend(
                self._split_foods(
                    row["Include"]
                )
            )

            avoid.extend(
                self._split_foods(
                    row["Avoid"]
                )
            )

        return {
            "condition": condition,
            "include": self._unique(include),
            "avoid": self._unique(avoid)
        }

    # =========================================================
    # SPLIT FOOD LIST
    # =========================================================

    def _split_foods(
        self,
        value
    ):

        if value is None:
            return []

        value = str(value).strip()

        if not value:
            return []

        # Handle comma, semicolon and pipe-separated data
        foods = re.split(
            r"[,;|]",
            value
        )

        return [
            food.strip()
            for food in foods
            if food.strip()
        ]

    # =========================================================
    # UNIQUE
    # =========================================================

    def _unique(
        self,
        values
    ):

        result = []

        seen = set()

        for value in values:

            key = value.lower()

            if key not in seen:

                seen.add(key)

                result.append(value)

        return result

    # =========================================================
    # FOOD CLASSIFIER
    # =========================================================

    def classify_food(
        self,
        food
    ):

        value = str(
            food
        ).lower()

        if any(
            x in value
            for x in [
                "oat",
                "idli",
                "dosa",
                "rice",
                "roti",
                "millet",
                "bread",
                "poha",
                "upma"
            ]
        ):

            return "carbohydrate"

        if any(
            x in value
            for x in [
                "egg",
                "chicken",
                "fish",
                "paneer",
                "tofu",
                "curd",
                "yogurt",
                "dal",
                "lentil",
                "chana",
                "rajma"
            ]
        ):

            return "protein"

        if any(
            x in value
            for x in [
                "vegetable",
                "spinach",
                "broccoli",
                "cucumber",
                "tomato",
                "cauliflower",
                "salad",
                "carrot",
                "beans"
            ]
        ):

            return "vegetable"

        if any(
            x in value
            for x in [
                "apple",
                "orange",
                "berry",
                "fruit",
                "guava"
            ]
        ):

            return "fruit"

        if any(
            x in value
            for x in [
                "nut",
                "almond",
                "walnut",
                "seed",
                "peanut"
            ]
        ):

            return "fat"

        return "other"

    # =========================================================
    # BUILD MEAL
    # =========================================================

    def build_meal(
        self,
        meal_name,
        included_foods
    ):

        classified = {
            "carbohydrate": [],
            "protein": [],
            "vegetable": [],
            "fruit": [],
            "fat": [],
            "other": []
        }

        for food in included_foods:

            category = self.classify_food(
                food
            )

            classified[
                category
            ].append(food)

        # Meal-specific selection
        if meal_name == "Breakfast":

            preferred_categories = [
                "carbohydrate",
                "protein",
                "fruit",
                "fat",
                "vegetable"
            ]

        elif meal_name == "Lunch":

            preferred_categories = [
                "vegetable",
                "protein",
                "carbohydrate",
                "fat"
            ]

        elif meal_name == "Snack":

            preferred_categories = [
                "fruit",
                "protein",
                "fat",
                "other"
            ]

        else:

            preferred_categories = [
                "vegetable",
                "protein",
                "carbohydrate",
                "fat"
            ]

        foods = []

        for category in preferred_categories:

            foods.extend(
                classified[category][:3]
            )

        return {
            "name": meal_name,
            "foods": self._unique(foods)[:6]
        }

    # =========================================================
    # GENERATE PLAN
    # =========================================================

    def generate_plan(
        self,
        diabetes_type=None,
        diet_preference=None
    ):

        condition_data = self.get_condition_data(
            diabetes_type
        )

        include = condition_data[
            "include"
        ]

        avoid = condition_data[
            "avoid"
        ]

        meals = [

            self.build_meal(
                "Breakfast",
                include
            ),

            self.build_meal(
                "Lunch",
                include
            ),

            self.build_meal(
                "Snack",
                include
            ),

            self.build_meal(
                "Dinner",
                include
            )

        ]

        return {

            "condition":
                condition_data["condition"],

            "diet_preference":
                diet_preference
                or "Balanced",

            "include":
                include,

            "avoid":
                avoid,

            "meals":
                meals

        }