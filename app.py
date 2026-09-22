from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    jsonify
)

from flask_sqlalchemy import SQLAlchemy

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from functools import wraps

from datetime import datetime, timedelta

import os
import csv
import math


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

app = Flask(__name__)

app.config["SECRET_KEY"] = (
    "smart-diabetes-mental-health-secret-key"
)

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATABASE_PATH = os.path.join(
    BASE_DIR,
    "smart_health.db"
)

DATA_DIR = os.path.join(
    BASE_DIR,
    "data"
)

app.config["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite:///" + DATABASE_PATH
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ============================================================
# DATABASE MODELS
# ============================================================

class User(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(150),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    diabetes_type = db.Column(
        db.String(30),
        default="Not specified"
    )

    age = db.Column(
        db.Integer,
        nullable=True
    )

    height = db.Column(
        db.Float,
        nullable=True
    )

    weight = db.Column(
        db.Float,
        nullable=True
    )

    activity_level = db.Column(
        db.String(50),
        default="Moderate"
    )

    goal = db.Column(
        db.String(100),
        default="General wellness"
    )

    profile_completed = db.Column(db.Boolean, default=False)
    onboarding_completed = db.Column(db.Boolean, default=False)
    gender = db.Column(db.String(50))
    years_since_diagnosis = db.Column(db.Integer)
    hba1c = db.Column(db.Float)
    current_medication = db.Column(db.String(255))
    blood_pressure = db.Column(db.String(50))
    cholesterol = db.Column(db.Float)
    smoking_status = db.Column(db.String(50))
    typical_sleep = db.Column(db.Float)
    typical_stress = db.Column(db.Integer)

    egfr = db.Column(db.Float, nullable=True)
    uacr = db.Column(db.Float, nullable=True)
    last_eye_exam = db.Column(db.String(50), nullable=True)
    retinopathy_status = db.Column(db.String(50), nullable=True)
    macular_edema = db.Column(db.String(50), nullable=True)



    health_records = db.relationship(
        "HealthRecord",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )


class HealthRecord(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    date = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    glucose = db.Column(
        db.Float,
        nullable=True
    )

    stress = db.Column(
        db.Float,
        nullable=True
    )

    sleep = db.Column(
        db.Float,
        nullable=True
    )

    steps = db.Column(
        db.Integer,
        nullable=True
    )

    weight = db.Column(
        db.Float,
        nullable=True
    )

    mood = db.Column(
        db.String(50),
        nullable=True
    )

    meal_context = db.Column(
        db.String(50),
        nullable=True
    )

    exercise_duration = db.Column(
        db.Float,
        nullable=True
    )

    is_valid = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    validation_notes = db.Column(
        db.String(255),
        nullable=True
    )

def validate_health_values(glucose=None, stress=None, sleep=None, steps=None, exercise_duration=None, weight=None):
    errors = []
    if glucose is not None and glucose != "":
        try:
            g = float(glucose)
            if g < 40.0 or g > 500.0:
                errors.append(f"Glucose value ({g} mg/dL) is outside valid physiological range (40 - 500 mg/dL).")
        except (ValueError, TypeError):
            errors.append("Glucose must be a valid number.")
            
    if stress is not None and stress != "":
        try:
            s = float(stress)
            if s < 1.0 or s > 10.0:
                errors.append(f"Stress level ({s}) must be between 1 and 10.")
        except (ValueError, TypeError):
            errors.append("Stress level must be a valid number.")
            
    if sleep is not None and sleep != "":
        try:
            sl = float(sleep)
            if sl < 0.5 or sl > 24.0:
                errors.append(f"Sleep hours ({sl}h) must be between 0.5 and 24 hours.")
        except (ValueError, TypeError):
            errors.append("Sleep hours must be a valid number.")
            
    if steps is not None and steps != "":
        try:
            st = int(float(steps))
            if st < 0 or st > 100000:
                errors.append("Steps must be between 0 and 100,000.")
        except (ValueError, TypeError):
            errors.append("Steps must be a valid integer.")
            
    if exercise_duration is not None and exercise_duration != "":
        try:
            ex = float(exercise_duration)
            if ex < 0 or ex > 720:
                errors.append("Exercise duration must be between 0 and 720 minutes.")
        except (ValueError, TypeError):
            errors.append("Exercise duration must be a valid number.")
            
    if weight is not None and weight != "":
        try:
            w = float(weight)
            if w < 20.0 or w > 400.0:
                errors.append("Weight must be between 20 and 400 kg.")
        except (ValueError, TypeError):
            errors.append("Weight must be a valid number.")
            
    return errors



# ============================================================
# DATABASE INITIALIZATION
# ============================================================

with app.app_context():

    db.create_all()


# ============================================================
# LOGIN DECORATOR
# ============================================================

def login_required(function):

    @wraps(function)
    def decorated_function(
        *args,
        **kwargs
    ):

        if "user_id" not in session:

            return redirect(
                url_for("login")
            )

        return function(
            *args,
            **kwargs
        )

    return decorated_function


# ============================================================
# CURRENT USER
# ============================================================


from functools import wraps

def onboarding_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return redirect(url_for('login'))
        if not user.profile_completed:
            return redirect(url_for('onboarding_profile'))
        if not user.onboarding_completed:
            return redirect(url_for('onboarding_history'))
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():

    user_id = session.get(
        "user_id"
    )

    if not user_id:

        return None

    return db.session.get(
        User,
        user_id
    )


# ============================================================
# SAFE TEXT
# ============================================================

def clean_text(value):

    if value is None:

        return ""

    return str(value).strip()


# ============================================================
# SAFE FLOAT
# ============================================================

def safe_float(value):

    try:

        if value is None:
            return None

        value = str(value).strip()

        if value == "":
            return None

        return float(value)

    except (
        ValueError,
        TypeError
    ):

        return None


# ============================================================
# SAFE INTEGER
# ============================================================

def safe_int(value):

    try:

        if value is None:
            return None

        value = str(value).strip()

        if value == "":
            return None

        return int(float(value))

    except (
        ValueError,
        TypeError
    ):

        return None


# ============================================================
# CSV READER
# ============================================================

def read_csv_file(filename):

    path = os.path.join(
        DATA_DIR,
        filename
    )

    if not os.path.exists(path):

        print(
            f"[WARNING] Missing dataset: {path}"
        )

        return []

    try:

        with open(
            path,
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as file:

            reader = csv.DictReader(
                file
            )

            rows = []

            for row in reader:

                cleaned = {}

                for key, value in row.items():

                    if key is None:
                        continue

                    cleaned[
                        str(key).strip()
                    ] = clean_text(value)

                rows.append(
                    cleaned
                )

            return rows

    except Exception as error:

        print(
            f"[CSV ERROR] {filename}: {error}"
        )

        return []


# ============================================================
# CONDITION MATCHING
# ============================================================

def condition_matches(
    condition,
    diabetes_type
):

    condition = clean_text(
        condition
    ).lower()

    diabetes_type = clean_text(
        diabetes_type
    ).lower()

    if not condition:

        return False

    if condition in (
        "general",
        "all",
        "both",
        "all types",
        "general wellness"
    ):

        return True

    if not diabetes_type:

        return False

    aliases = {

        "type 1": [
            "type 1",
            "type1",
            "t1",
            "type 1 diabetes"
        ],

        "type 2": [
            "type 2",
            "type2",
            "t2",
            "type 2 diabetes"
        ]

    }

    selected_aliases = aliases.get(
        diabetes_type,
        [diabetes_type]
    )

    return (
        condition in selected_aliases
        or diabetes_type in condition
        or condition in diabetes_type
    )


# ============================================================
# DIET RECOMMENDATIONS
# ============================================================

def get_diet_recommendations(user):

    rows = read_csv_file(
        "diet.csv"
    )

    if not rows:

        return []

    diabetes_type = (
        user.diabetes_type
        or "General"
    )

    matched = []

    # --------------------------------------------------------
    # First pass: exact/general matches
    # --------------------------------------------------------

    for row in rows:

        condition = clean_text(
            row.get("Condition")
        )

        if condition_matches(
            condition,
            diabetes_type
        ):

            item = {

                "condition":
                    condition,

                "meal":
                    clean_text(
                        row.get("Meal")
                    ),

                "food":
                    clean_text(
                        row.get("Food")
                    ),

                "serving_grams":
                    clean_text(
                        row.get(
                            "Serving_grams"
                        )
                    ),

                "calories":
                    clean_text(
                        row.get(
                            "Calories"
                        )
                    ),

                "carbs":
                    clean_text(
                        row.get(
                            "Carbs_g"
                        )
                    ),

                "protein":
                    clean_text(
                        row.get(
                            "Protein_g"
                        )
                    ),

                "fat":
                    clean_text(
                        row.get(
                            "Fat_g"
                        )
                    ),

                "fiber":
                    clean_text(
                        row.get(
                            "Fiber_g"
                        )
                    ),

                "include":
                    clean_text(
                        row.get(
                            "Include"
                        )
                    ),

                "avoid":
                    clean_text(
                        row.get(
                            "Avoid"
                        )
                    ),

                "notes":
                    clean_text(
                        row.get(
                            "Notes"
                        )
                    )

            }

            matched.append(
                item
            )

    # --------------------------------------------------------
    # Fallback to General if no match
    # --------------------------------------------------------

    if not matched:

        for row in rows:

            condition = clean_text(
                row.get("Condition")
            )

            if condition.lower() in (
                "general",
                "all",
                "both"
            ):

                matched.append({

                    "condition":
                        condition,

                    "meal":
                        clean_text(
                            row.get("Meal")
                        ),

                    "food":
                        clean_text(
                            row.get("Food")
                        ),

                    "serving_grams":
                        clean_text(
                            row.get(
                                "Serving_grams"
                            )
                        ),

                    "calories":
                        clean_text(
                            row.get(
                                "Calories"
                            )
                        ),

                    "carbs":
                        clean_text(
                            row.get(
                                "Carbs_g"
                            )
                        ),

                    "protein":
                        clean_text(
                            row.get(
                                "Protein_g"
                            )
                        ),

                    "fat":
                        clean_text(
                            row.get(
                                "Fat_g"
                            )
                        ),

                    "fiber":
                        clean_text(
                            row.get(
                                "Fiber_g"
                            )
                        ),

                    "include":
                        clean_text(
                            row.get(
                                "Include"
                            )
                        ),

                    "avoid":
                        clean_text(
                            row.get(
                                "Avoid"
                            )
                        ),

                    "notes":
                        clean_text(
                            row.get(
                                "Notes"
                            )
                        )

                })

    return matched


# ============================================================
# NUTRITION MEAL NORMALIZATION
# ============================================================

def normalize_meal_name(meal):

    meal = clean_text(
        meal
    ).lower()

    replacements = {

        "breakfast":
            "Breakfast",

        "morning":
            "Breakfast",

        "brunch":
            "Breakfast",

        "lunch":
            "Lunch",

        "midday":
            "Lunch",

        "snack":
            "Snack",

        "snacks":
            "Snack",

        "evening snack":
            "Snack",

        "dinner":
            "Dinner",

        "night":
            "Dinner",

        "supper":
            "Dinner"

    }

    return replacements.get(
        meal,
        meal.title()
        if meal
        else "Other"
    )


# ============================================================
# BUILD ADVANCED MEAL PLAN
# ============================================================

def build_meal_plan(
    recommendations
):

    meal_plan = {

        "Breakfast": {

            "foods": [],

            "description":
                "A balanced morning meal with appropriate carbohydrate, protein and fiber.",

            "tip":
                "Pair carbohydrate-containing foods with protein and fiber."

        },

        "Lunch": {

            "foods": [],

            "description":
                "Build lunch around vegetables, protein and an appropriate carbohydrate portion.",

            "tip":
                "Make non-starchy vegetables a major part of the meal."

        },

        "Snack": {

            "foods": [],

            "description":
                "A practical snack option based on the available nutrition dataset.",

            "tip":
                "Prefer nutrient-dense foods and avoid sugar-sweetened drinks."

        },

        "Dinner": {

            "foods": [],

            "description":
                "A balanced evening meal with vegetables, protein and controlled carbohydrate portions.",

            "tip":
                "Avoid making dinner predominantly refined carbohydrate."

        }

    }


    # --------------------------------------------------------
    # Add dataset foods
    # --------------------------------------------------------

    for item in recommendations:

        meal_name = normalize_meal_name(
            item.get("meal")
        )

        food_name = clean_text(
            item.get("food")
        )

        # ----------------------------------------------------
        # Advanced dataset
        # ----------------------------------------------------

        if food_name:

            if meal_name not in meal_plan:

                meal_name = "Breakfast"

            food_object = {

                "name":
                    food_name,

                "portion":
                    item.get(
                        "serving_grams"
                    )
                    or "As planned",

                "calories":
                    item.get(
                        "calories"
                    ),

                "carbs":
                    item.get(
                        "carbs"
                    ),

                "protein":
                    item.get(
                        "protein"
                    ),

                "fiber":
                    item.get(
                        "fiber"
                    ),

                "fat":
                    item.get(
                        "fat"
                    ),

                "notes":
                    item.get(
                        "notes"
                    )

            }

            meal_plan[
                meal_name
            ][
                "foods"
            ].append(
                food_object
            )

        # ----------------------------------------------------
        # Simple dataset
        # Condition, Include, Avoid
        # ----------------------------------------------------

        elif item.get("include"):

            include_text = clean_text(
                item.get("include")
            )

            if meal_name not in meal_plan:

                meal_name = "Breakfast"

            # Split common separators
            pieces = []

            for separator in (
                ",",
                ";",
                "|"
            ):

                if separator in include_text:

                    pieces = [
                        clean_text(x)
                        for x
                        in include_text.split(
                            separator
                        )
                        if clean_text(x)
                    ]

                    break

            if not pieces:

                pieces = [
                    include_text
                ]

            for food in pieces:

                meal_plan[
                    meal_name
                ][
                    "foods"
                ].append({

                    "name":
                        food,

                    "portion":
                        "Recommended",

                    "calories":
                        "",

                    "carbs":
                        "",

                    "protein":
                        "",

                    "fiber":
                        "",

                    "fat":
                        "",

                    "notes":
                        ""

                })


    return meal_plan


# ============================================================
# FLATTEN MEAL DATA FOR TEMPLATE COMPATIBILITY
# ============================================================

def enrich_meal_plan(
    meal_plan
):

    for meal_name, meal in meal_plan.items():

        unique_foods = []

        seen = set()

        for food in meal["foods"]:

            name = clean_text(
                food.get("name")
            )

            if not name:
                continue

            key = name.lower()

            if key in seen:
                continue

            seen.add(key)

            unique_foods.append(
                food
            )

        meal["foods"] = unique_foods

    return meal_plan


# ============================================================
# WORKOUT RECOMMENDATIONS
# ============================================================

def get_workout_recommendations(
    user
):

    rows = read_csv_file(
        "workout.csv"
    )

    if not rows:

        return []

    diabetes_type = (
        user.diabetes_type
        or "General"
    )

    recommendations = []


    for row in rows:

        condition = clean_text(
            row.get("Condition")
        )

        if not condition_matches(
            condition,
            diabetes_type
        ):

            continue

        exercise = (
            clean_text(
                row.get("Exercise")
            )
            or
            clean_text(
                row.get("Workout")
            )
        )

        item = {

            "condition":
                condition,

            "exercise":
                exercise,

            "workout":
                exercise,

            "category":
                clean_text(
                    row.get(
                        "Category"
                    )
                ),

            "duration":
                clean_text(
                    row.get(
                        "Duration_min"
                    )
                ),

            "sets":
                clean_text(
                    row.get(
                        "Sets"
                    )
                ),

            "reps":
                clean_text(
                    row.get(
                        "Reps"
                    )
                ),

            "intensity":
                clean_text(
                    row.get(
                        "Intensity"
                    )
                ),

            "rest":
                clean_text(
                    row.get(
                        "Rest_sec"
                    )
                ),

            "level":
                clean_text(
                    row.get(
                        "Level"
                    )
                ),

            "notes":
                clean_text(
                    row.get(
                        "Notes"
                    )
                ),

            "type1_safety":
                clean_text(
                    row.get(
                        "Type1_Safety"
                    )
                ),

            "type2_safety":
                clean_text(
                    row.get(
                        "Type2_Safety"
                    )
                )

        }

        recommendations.append(
            item
        )


    # --------------------------------------------------------
    # General fallback
    # --------------------------------------------------------

    if not recommendations:

        for row in rows:

            condition = clean_text(
                row.get("Condition")
            )

            if condition.lower() in (
                "general",
                "all",
                "both"
            ):

                exercise = (
                    clean_text(
                        row.get(
                            "Exercise"
                        )
                    )
                    or
                    clean_text(
                        row.get(
                            "Workout"
                        )
                    )
                )

                recommendations.append({

                    "condition":
                        condition,

                    "exercise":
                        exercise,

                    "workout":
                        exercise,

                    "category":
                        clean_text(
                            row.get(
                                "Category"
                            )
                        ),

                    "duration":
                        clean_text(
                            row.get(
                                "Duration_min"
                            )
                        ),

                    "sets":
                        clean_text(
                            row.get(
                                "Sets"
                            )
                        ),

                    "reps":
                        clean_text(
                            row.get(
                                "Reps"
                            )
                        ),

                    "intensity":
                        clean_text(
                            row.get(
                                "Intensity"
                            )
                        ),

                    "rest":
                        clean_text(
                            row.get(
                                "Rest_sec"
                            )
                        ),

                    "level":
                        clean_text(
                            row.get(
                                "Level"
                            )
                        ),

                    "notes":
                        clean_text(
                            row.get(
                                "Notes"
                            )
                        ),

                    "type1_safety":
                        clean_text(
                            row.get(
                                "Type1_Safety"
                            )
                        ),

                    "type2_safety":
                        clean_text(
                            row.get(
                                "Type2_Safety"
                            )
                        )

                })


    return recommendations


# ============================================================
# HEALTH INTELLIGENCE
# ============================================================

def calculate_health_intelligence(
    record
):

    if not record:

        return {

            "score": 0,

            "status":
                "No data",

            "mental_score":
                None,

            "lifestyle_score":
                None,

            "recommendations":
                [
                    "Start recording your health indicators to build your personal trend."
                ],

            "flags":
                [],

            "glucose_status":
                "No reading",

            "stress_status":
                "No reading",

            "sleep_status":
                "No reading",

            "activity_status":
                "No reading"

        }


    score_components = []

    lifestyle_components = []

    recommendations = []

    flags = []


    # ========================================================
    # GLUCOSE
    # ========================================================

    glucose_score = None

    glucose_status = "No reading"


    if record.glucose is not None:

        glucose = float(
            record.glucose
        )


        if glucose < 70:

            glucose_score = 35

            glucose_status = "Low"

            flags.append(
                "Recorded glucose is below 70 mg/dL. Follow your personal diabetes plan for low glucose and seek appropriate medical advice if needed."
            )


        elif glucose <= 140:

            glucose_score = 100

            glucose_status = "Within tracked range"


        elif glucose <= 180:

            glucose_score = 75

            glucose_status = "Elevated"

            recommendations.append(
                "Your recorded glucose is elevated. Continue tracking patterns and discuss repeated elevations with your healthcare professional."
            )


        else:

            glucose_score = 45

            glucose_status = "High"

            flags.append(
                "Your recorded glucose is elevated. Repeated high readings should be discussed with a qualified healthcare professional."
            )


        score_components.append(
            glucose_score
        )


    # ========================================================
    # STRESS / MENTAL WELLNESS
    # ========================================================

    mental_score = None

    stress_status = "No reading"


    if record.stress is not None:

        stress = max(
            0,
            min(
                100,
                float(record.stress)
            )
        )

        mental_score = round(
            100 - stress
        )


        if stress < 30:

            stress_status = "Low"

        elif stress < 60:

            stress_status = "Moderate"

        elif stress < 80:

            stress_status = "High"

            flags.append(
                "Reported stress is high. Consider recovery, relaxation, social support and professional support when appropriate."
            )

        else:

            stress_status = "Very high"

            flags.append(
                "Reported stress is very high. Consider reaching out to a qualified mental-health professional or trusted support person."
            )


        score_components.append(
            mental_score
        )


    # ========================================================
    # SLEEP
    # ========================================================

    sleep_score = None

    sleep_status = "No reading"


    if record.sleep is not None:

        sleep = max(
            0,
            float(record.sleep)
        )


        if sleep >= 7:

            sleep_score = 100

            sleep_status = "Good"


        elif sleep >= 6:

            sleep_score = 80

            sleep_status = "Moderate"


        elif sleep >= 5:

            sleep_score = 60

            sleep_status = "Low"


        else:

            sleep_score = 40

            sleep_status = "Very low"

            recommendations.append(
                "Your recorded sleep duration is low. Prioritize a consistent sleep routine."
            )


        lifestyle_components.append(
            sleep_score
        )


    # ========================================================
    # ACTIVITY
    # ========================================================

    activity_score = None

    activity_status = "No reading"


    if record.steps is not None:

        steps = max(
            0,
            int(record.steps)
        )


        if steps >= 10000:

            activity_score = 100

            activity_status = "Excellent"


        elif steps >= 7500:

            activity_score = 90

            activity_status = "Active"


        elif steps >= 5000:

            activity_score = 75

            activity_status = "Moderate"


        elif steps >= 2500:

            activity_score = 55

            activity_status = "Low"


        else:

            activity_score = 35

            activity_status = "Very low"


        lifestyle_components.append(
            activity_score
        )


        if steps < 5000:

            recommendations.append(
                "Your recorded step count is relatively low. Consider adding comfortable movement throughout the day if appropriate for you."
            )


    # ========================================================
    # LIFESTYLE SCORE
    # ========================================================

    lifestyle_score = None


    if lifestyle_components:

        lifestyle_score = round(
            sum(
                lifestyle_components
            )
            /
            len(
                lifestyle_components
            )
        )


        score_components.append(
            lifestyle_score
        )


    # ========================================================
    # FINAL SCORE
    # ========================================================

    if score_components:

        score = round(
            sum(
                score_components
            )
            /
            len(
                score_components
            )
        )

    else:

        score = 0


    # ========================================================
    # STATUS
    # ========================================================

    if score >= 80:

        status = "On Track"

    elif score >= 60:

        status = "Needs Attention"

    else:

        status = "Needs Improvement"


    # ========================================================
    # DEFAULT RECOMMENDATION
    # ========================================================

    if not recommendations:

        recommendations.append(
            "Keep recording your health indicators regularly so DiaMind can identify meaningful patterns."
        )


    return {

        "score":
            score,

        "status":
            status,

        "mental_score":
            mental_score,

        "lifestyle_score":
            lifestyle_score,

        "recommendations":
            recommendations,

        "flags":
            flags,

        "glucose_status":
            glucose_status,

        "stress_status":
            stress_status,

        "sleep_status":
            sleep_status,

        "activity_status":
            activity_status

    }


# ============================================================
# SERIALIZE HEALTH RECORD
# ============================================================

def serialize_record(
    record
):

    return {

        "id":
            record.id,

        "date":
            record.date.strftime(
                "%Y-%m-%d"
            ),

        "glucose":
            record.glucose,

        "stress":
            record.stress,

        "sleep":
            record.sleep,

        "steps":
            record.steps,

        "weight":
            record.weight,

        "mood":
            record.mood

    }


# ============================================================
# HEALTH TREND SUMMARY
# ============================================================

def calculate_trend_summary(
    records
):

    glucose_values = [
        r.glucose
        for r in records
        if r.glucose is not None
    ]

    stress_values = [
        r.stress
        for r in records
        if r.stress is not None
    ]

    sleep_values = [
        r.sleep
        for r in records
        if r.sleep is not None
    ]

    step_values = [
        r.steps
        for r in records
        if r.steps is not None
    ]


    def average(values):

        if not values:
            return None

        return round(
            sum(values)
            /
            len(values),
            1
        )


    def minimum(values):

        if not values:
            return None

        return min(values)


    def maximum(values):

        if not values:
            return None

        return max(values)


    return {

        "glucose": {

            "average":
                average(
                    glucose_values
                ),

            "minimum":
                minimum(
                    glucose_values
                ),

            "maximum":
                maximum(
                    glucose_values
                ),

            "count":
                len(
                    glucose_values
                )

        },

        "stress": {

            "average":
                average(
                    stress_values
                ),

            "minimum":
                minimum(
                    stress_values
                ),

            "maximum":
                maximum(
                    stress_values
                ),

            "count":
                len(
                    stress_values
                )

        },

        "sleep": {

            "average":
                average(
                    sleep_values
                ),

            "minimum":
                minimum(
                    sleep_values
                ),

            "maximum":
                maximum(
                    sleep_values
                ),

            "count":
                len(
                    sleep_values
                )

        },

        "steps": {

            "average":
                average(
                    step_values
                ),

            "minimum":
                minimum(
                    step_values
                ),

            "maximum":
                maximum(
                    step_values
                ),

            "count":
                len(
                    step_values
                )

        }

    }



# ============================================================
# ADVANCED DIA-MIND INTELLIGENCE LAYER
# ============================================================
# These functions are intentionally self-contained so the project can
# continue working with the current templates and CSV files.
#
# IMPORTANT:
# This is an educational monitoring/recommendation system, not a
# diagnostic or treatment system. It should not replace a clinician,
# individualized diabetes plan, medication instructions, or emergency care.
# ============================================================

def normalize_diabetes_type(value):
    """Normalize common diabetes-type labels."""
    value = clean_text(value).lower()

    if value in ("type 1", "type1", "t1", "type 1 diabetes"):
        return "Type 1"

    if value in ("type 2", "type2", "t2", "type 2 diabetes"):
        return "Type 2"

    if value in ("prediabetes", "pre-diabetes"):
        return "Prediabetes"

    return "Not specified"


def dataset_info(filename):
    """Return useful diagnostics for a CSV dataset."""
    path = os.path.join(DATA_DIR, filename)

    if not os.path.exists(path):
        return {
            "file": filename,
            "exists": False,
            "rows": 0,
            "columns": [],
            "error": "File not found"
        }

    rows = read_csv_file(filename)

    columns = []
    if rows:
        columns = list(rows[0].keys())

    return {
        "file": filename,
        "exists": True,
        "rows": len(rows),
        "columns": columns,
        "error": None
    }


def safe_percentage(part, total):
    """Safe percentage calculation."""
    if total in (None, 0):
        return 0

    try:
        return round((float(part) / float(total)) * 100, 1)
    except (TypeError, ValueError, ZeroDivisionError):
        return 0


def calculate_bmi(weight, height_cm):
    """Calculate BMI when valid height and weight exist."""
    weight = safe_float(weight)
    height_cm = safe_float(height_cm)

    if not weight or not height_cm or height_cm <= 0:
        return None

    height_m = height_cm / 100.0
    return round(weight / (height_m ** 2), 1)


def bmi_category(bmi):
    """Educational BMI category helper."""
    if bmi is None:
        return "Unavailable"

    if bmi < 18.5:
        return "Below reference range"

    if bmi < 25:
        return "Reference range"

    if bmi < 30:
        return "Above reference range"

    return "High BMI range"


def calculate_personal_baseline(records, field, limit=14):
    """Return average/min/max for a recent metric."""
    values = []

    for record in records[-limit:]:
        value = getattr(record, field, None)

        if value is not None:
            try:
                values.append(float(value))
            except (TypeError, ValueError):
                pass

    if not values:
        return {
            "count": 0,
            "average": None,
            "minimum": None,
            "maximum": None
        }

    return {
        "count": len(values),
        "average": round(sum(values) / len(values), 1),
        "minimum": min(values),
        "maximum": max(values)
    }


def detect_metric_anomalies(records, field, minimum_samples=3):
    """
    Lightweight personal-baseline anomaly detector.
    It compares a recent reading with the user's own recent average.
    It is not a medical diagnostic model.
    """
    values = []

    for record in records:
        value = getattr(record, field, None)

        if value is not None:
            try:
                values.append((record, float(value)))
            except (TypeError, ValueError):
                pass

    if len(values) < minimum_samples:
        return []

    recent_record, recent_value = values[-1]
    previous = [value for _, value in values[:-1]]

    if not previous:
        return []

    baseline = sum(previous) / len(previous)

    if baseline == 0:
        return []

    deviation = ((recent_value - baseline) / abs(baseline)) * 100

    severity = "normal"

    if abs(deviation) >= 50:
        severity = "high"
    elif abs(deviation) >= 25:
        severity = "moderate"

    if severity == "normal":
        return []

    return [{
        "metric": field,
        "value": recent_value,
        "personal_baseline": round(baseline, 1),
        "deviation_percent": round(deviation, 1),
        "severity": severity,
        "date": recent_record.date.strftime("%Y-%m-%d")
        if recent_record.date else None
    }]


def build_pattern_insights(records):
    """Find simple longitudinal patterns from recorded data."""
    insights = []

    if len(records) < 2:
        return insights

    # Glucose direction
    glucose = [
        float(r.glucose)
        for r in records
        if r.glucose is not None
    ]

    if len(glucose) >= 2:
        first = glucose[0]
        last = glucose[-1]

        if last < first:
            insights.append({
                "type": "positive",
                "title": "Glucose trend",
                "message": "Your latest recorded glucose is lower than your first recorded value."
            })
        elif last > first:
            insights.append({
                "type": "attention",
                "title": "Glucose trend",
                "message": "Your latest recorded glucose is higher than your first recorded value. Look for repeated patterns rather than judging from one reading."
            })

    # Stress direction
    stress = [
        float(r.stress)
        for r in records
        if r.stress is not None
    ]

    if len(stress) >= 2:
        if stress[-1] < stress[0]:
            insights.append({
                "type": "positive",
                "title": "Stress trend",
                "message": "Your latest recorded stress score is lower than your first recorded score."
            })
        elif stress[-1] > stress[0]:
            insights.append({
                "type": "attention",
                "title": "Stress trend",
                "message": "Your latest recorded stress score is higher than your first recorded score."
            })

    # Sleep/activity relationship
    pairs = [
        (r.sleep, r.steps)
        for r in records
        if r.sleep is not None and r.steps is not None
    ]

    if len(pairs) >= 3:
        active_sleep = [
            sleep for sleep, steps in pairs
            if steps >= 7500
        ]

        lower_activity_sleep = [
            sleep for sleep, steps in pairs
            if steps < 7500
        ]

        if active_sleep and lower_activity_sleep:
            active_avg = sum(active_sleep) / len(active_sleep)
            lower_avg = sum(lower_activity_sleep) / len(lower_activity_sleep)

            if active_avg > lower_avg + 0.5:
                insights.append({
                    "type": "pattern",
                    "title": "Activity and sleep pattern",
                    "message": "Your recorded days with higher activity also show somewhat longer sleep. This is an observation from your logged data, not proof of causation."
                })

    return insights


def build_personalized_health_profile(user, records):
    """Build a single object that can be passed to dashboards."""
    latest = records[-1] if records else None

    bmi = calculate_bmi(
        user.weight,
        user.height
    )

    baselines = {
        "glucose": calculate_personal_baseline(records, "glucose"),
        "stress": calculate_personal_baseline(records, "stress"),
        "sleep": calculate_personal_baseline(records, "sleep"),
        "steps": calculate_personal_baseline(records, "steps"),
        "weight": calculate_personal_baseline(records, "weight")
    }

    anomalies = []
    anomalies.extend(
        detect_metric_anomalies(records, "glucose")
    )
    anomalies.extend(
        detect_metric_anomalies(records, "stress")
    )
    anomalies.extend(
        detect_metric_anomalies(records, "sleep")
    )
    anomalies.extend(
        detect_metric_anomalies(records, "steps")
    )

    return {
        "diabetes_type": normalize_diabetes_type(
            user.diabetes_type
        ),
        "age": user.age,
        "height_cm": user.height,
        "weight_kg": user.weight,
        "bmi": bmi,
        "bmi_category": bmi_category(bmi),
        "activity_level": user.activity_level,
        "goal": user.goal,
        "baselines": baselines,
        "anomalies": anomalies,
        "patterns": build_pattern_insights(records),
        "latest": serialize_record(latest) if latest else None
    }


def build_safety_guidance(user, latest_record):
    """
    General safety-oriented guidance. Values are deliberately framed as
    prompts for attention rather than diagnoses or treatment instructions.
    """
    guidance = []

    diabetes_type = normalize_diabetes_type(
        user.diabetes_type
    )

    if diabetes_type == "Type 1":
        guidance.append(
            "For Type 1 diabetes, exercise and food choices should be coordinated with the person's established diabetes-management plan, including glucose monitoring and prescribed insulin."
        )

    elif diabetes_type == "Type 2":
        guidance.append(
            "For Type 2 diabetes, regular activity, balanced meals and glucose tracking can support self-management, but individual targets should come from the person's healthcare team."
        )

    else:
        guidance.append(
            "Use the dashboard as a tracking and education tool and confirm individualized targets with a qualified healthcare professional."
        )

    if latest_record:
        if latest_record.glucose is not None:
            if latest_record.glucose < 70:
                guidance.append(
                    "The latest recorded glucose is below 70 mg/dL. Follow the person's established hypoglycemia plan and seek appropriate medical help when needed."
                )
            elif latest_record.glucose >= 250:
                guidance.append(
                    "The latest recorded glucose is substantially elevated. Repeated or concerning readings should be discussed with the person's diabetes-care team."
                )

        if latest_record.stress is not None and latest_record.stress >= 80:
            guidance.append(
                "The latest reported stress score is very high. Consider support from a qualified mental-health professional if distress persists or interferes with daily life."
            )

    return guidance


def build_weekly_activity_plan(user):
    """
    Creates an educational weekly structure rather than a medical prescription.
    The 150-minute reference is a general adult activity guideline; users with
    diabetes should individualize exercise with their healthcare team.
    """
    activity = clean_text(user.activity_level).lower()

    if "low" in activity or "sedentary" in activity:
        aerobic = 120
    elif "high" in activity or "active" in activity:
        aerobic = 180
    else:
        aerobic = 150

    return {
        "aerobic_minutes_reference": aerobic,
        "strength_days_reference": 2,
        "mobility_days_reference": 3,
        "recovery_days_reference": 1,
        "note": "Reference plan only. Adjust intensity, duration and safety requirements to the person's condition and clinician guidance."
    }


def build_nutrition_intelligence(user, recommendations):
    """Create meal-wise nutrition totals and practical metadata."""
    meals = build_meal_plan(recommendations)
    meals = enrich_meal_plan(meals)

    totals = {
        "calories": 0.0,
        "carbs": 0.0,
        "protein": 0.0,
        "fiber": 0.0,
        "fat": 0.0
    }

    meal_totals = {}

    for meal_name, meal in meals.items():
        meal_total = {
            "calories": 0.0,
            "carbs": 0.0,
            "protein": 0.0,
            "fiber": 0.0,
            "fat": 0.0,
            "food_count": len(meal.get("foods", []))
        }

        for food in meal.get("foods", []):
            for key in (
                "calories",
                "carbs",
                "protein",
                "fiber",
                "fat"
            ):
                value = safe_float(food.get(key))
                if value is not None:
                    meal_total[key] += value
                    totals[key] += value

        meal_totals[meal_name] = {
            key: round(value, 1)
            if isinstance(value, (int, float))
            else value
            for key, value in meal_total.items()
        }

    diabetes_type = normalize_diabetes_type(
        user.diabetes_type
    )

    principles = [
        "Prefer minimally processed foods and include vegetables, protein and fiber where appropriate.",
        "Use the portion sizes in the dataset as planning references rather than assuming one portion fits everyone.",
        "Avoid treating a single food as a cure or guaranteed method for controlling diabetes."
    ]

    if diabetes_type == "Type 1":
        principles.append(
            "Carbohydrate amounts can be particularly important for people using insulin; use the person's established carbohydrate-counting and insulin plan."
        )

    if diabetes_type == "Type 2":
        principles.append(
            "Consistent meal patterns and appropriate portions can support glucose management, but individualized carbohydrate and calorie targets should be confirmed with a professional."
        )

    return {
        "meals": meals,
        "meal_totals": meal_totals,
        "totals": {
            key: round(value, 1)
            for key, value in totals.items()
        },
        "principles": principles
    }


def build_workout_intelligence(user, recommendations):
    """Organize workout dataset rows into a richer UI-ready structure."""
    categories = {}

    for item in recommendations:
        category = clean_text(
            item.get("category")
        ) or "General"

        categories.setdefault(
            category,
            []
        ).append(item)

    weekly = build_weekly_activity_plan(user)

    type_name = normalize_diabetes_type(
        user.diabetes_type
    )

    safety_key = (
        "type1_safety"
        if type_name == "Type 1"
        else "type2_safety"
        if type_name == "Type 2"
        else None
    )

    for item in recommendations:
        item["safety"] = (
            item.get(safety_key, "")
            if safety_key
            else ""
        )

    return {
        "recommendations": recommendations,
        "categories": categories,
        "weekly_reference": weekly,
        "count": len(recommendations)
    }


def build_dashboard_intelligence(user, records_db):
    """One consolidated intelligence payload for the dashboard."""
    latest = records_db[-1] if records_db else None

    health = calculate_health_intelligence(latest)

    profile = build_personalized_health_profile(
        user,
        records_db
    )

    diet_rows = get_diet_recommendations(user)
    workout_rows = get_workout_recommendations(user)

    nutrition = build_nutrition_intelligence(
        user,
        diet_rows
    )

    workouts = build_workout_intelligence(
        user,
        workout_rows
    )

    return {
        "health": health,
        "profile": profile,
        "nutrition": nutrition,
        "workouts": workouts,
        "safety_guidance": build_safety_guidance(
            user,
            latest
        ),
        "trend_summary": calculate_trend_summary(
            records_db
        )
    }


def exportable_health_report(user, records_db):
    """Return structured data suitable for a future PDF/CSV export."""
    intelligence = build_dashboard_intelligence(
        user,
        records_db
    )

    return {
        "generated_at": datetime.utcnow().isoformat(),
        "patient": {
            "name": user.name,
            "email": user.email,
            "diabetes_type": normalize_diabetes_type(
                user.diabetes_type
            ),
            "age": user.age,
            "height_cm": user.height,
            "weight_kg": user.weight
        },
        "intelligence": intelligence,
        "records": [
            serialize_record(r)
            for r in records_db
        ]
    }


# ============================================================
# ADVANCED DASHBOARD API
# ============================================================

@app.route("/api/intelligence")
@login_required
def intelligence_api():
    user = get_current_user()

    records = (
        HealthRecord.query
        .filter_by(user_id=user.id)
        .order_by(HealthRecord.date.asc())
        .all()
    )

    return jsonify({
        "status": "success",
        "data": build_dashboard_intelligence(
            user,
            records
        )
    })


@app.route("/api/profile-intelligence")
@login_required
def profile_intelligence_api():
    user = get_current_user()

    records = (
        HealthRecord.query
        .filter_by(user_id=user.id)
        .order_by(HealthRecord.date.asc())
        .all()
    )

    return jsonify({
        "status": "success",
        "profile": build_personalized_health_profile(
            user,
            records
        )
    })


@app.route("/api/patterns")
@login_required
def patterns_api():
    user = get_current_user()

    records = (
        HealthRecord.query
        .filter_by(user_id=user.id)
        .order_by(HealthRecord.date.asc())
        .all()
    )

    return jsonify({
        "status": "success",
        "patterns": build_pattern_insights(records)
    })


@app.route("/api/anomalies")
@login_required
def anomalies_api():
    user = get_current_user()

    records = (
        HealthRecord.query
        .filter_by(user_id=user.id)
        .order_by(HealthRecord.date.asc())
        .all()
    )

    anomalies = []

    for field in (
        "glucose",
        "stress",
        "sleep",
        "steps",
        "weight"
    ):
        anomalies.extend(
            detect_metric_anomalies(
                records,
                field
            )
        )

    return jsonify({
        "status": "success",
        "anomalies": anomalies,
        "count": len(anomalies)
    })


@app.route("/api/weekly-plan")
@login_required
def weekly_plan_api():
    user = get_current_user()

    return jsonify({
        "status": "success",
        "plan": build_weekly_activity_plan(user)
    })


@app.route("/api/nutrition-intelligence")
@login_required
def nutrition_intelligence_api():
    user = get_current_user()

    recommendations = get_diet_recommendations(user)

    return jsonify({
        "status": "success",
        "data": build_nutrition_intelligence(
            user,
            recommendations
        )
    })


@app.route("/api/workout-intelligence")
@login_required
def workout_intelligence_api():
    user = get_current_user()

    recommendations = get_workout_recommendations(user)

    return jsonify({
        "status": "success",
        "data": build_workout_intelligence(
            user,
            recommendations
        )
    })


@app.route("/api/report")
@login_required
def report_api():
    user = get_current_user()

    records = (
        HealthRecord.query
        .filter_by(user_id=user.id)
        .order_by(HealthRecord.date.asc())
        .all()
    )

    return jsonify(
        exportable_health_report(
            user,
            records
        )
    )


@app.route("/api/datasets")
@login_required
def datasets_api():
    return jsonify({
        "status": "success",
        "datasets": {
            "diabetes": dataset_info("diabetes.csv"),
            "diet": dataset_info("diet.csv"),
            "workout": dataset_info("workout.csv")
        }
    })


@app.route("/api/recent-records")
@login_required
def recent_records_api():
    user = get_current_user()

    try:
        limit = int(
            request.args.get(
                "limit",
                10
            )
        )
    except (TypeError, ValueError):
        limit = 10

    limit = max(1, min(limit, 100))

    records = (
        HealthRecord.query
        .filter_by(user_id=user.id)
        .order_by(HealthRecord.date.desc())
        .limit(limit)
        .all()
    )

    return jsonify({
        "status": "success",
        "records": [
            serialize_record(r)
            for r in reversed(records)
        ]
    })


@app.route("/api/health-summary")
@login_required
def health_summary_api():
    user = get_current_user()

    records = (
        HealthRecord.query
        .filter_by(user_id=user.id)
        .order_by(HealthRecord.date.asc())
        .all()
    )

    latest = records[-1] if records else None

    return jsonify({
        "status": "success",
        "score": calculate_health_intelligence(
            latest
        ),
        "summary": calculate_trend_summary(
            records
        ),
        "profile": build_personalized_health_profile(
            user,
            records
        )
    })



# ============================================================
# HOME
# ============================================================

@app.route('/')
def index():
    return render_template('landing.html')
@app.route(
    "/register",
    methods=[
        "GET",
        "POST"
    ]
)
def register():

    if request.method == "POST":

        name = clean_text(
            request.form.get(
                "name"
            )
        )

        email = clean_text(
            request.form.get(
                "email"
            )
        ).lower()

        password = request.form.get(
            "password",
            ""
        )


        if (
            not name
            or not email
            or not password
        ):

            flash(
                "Please fill all required fields.",
                "error"
            )

            return redirect(
                url_for(
                    "register"
                )
            )


        existing_user = (
            User.query
            .filter_by(
                email=email
            )
            .first()
        )


        if existing_user:

            flash(
                "An account with this email already exists.",
                "error"
            )

            return redirect(
                url_for(
                    "login"
                )
            )


        user = User(

            name=name,

            email=email,

            password=
                generate_password_hash(
                    password
                )

        )


        db.session.add(
            user
        )

        db.session.commit()


        session[
            "user_id"
        ] = user.id


        return redirect(
            url_for(
                "dashboard"
            )
        )


    return render_template(
        "register.html"
    )


# ============================================================
# LOGIN
# ============================================================

@app.route(
    "/login",
    methods=[
        "GET",
        "POST"
    ]
)
def login():

    if request.method == "POST":

        email = clean_text(
            request.form.get(
                "email"
            )
        ).lower()

        password = request.form.get(
            "password",
            ""
        )


        user = (
            User.query
            .filter_by(
                email=email
            )
            .first()
        )


        if (
            user
            and check_password_hash(
                user.password,
                password
            )
        ):

            session[
                "user_id"
            ] = user.id

            return redirect(
                url_for(
                    "dashboard"
                )
            )


        flash(
            "Invalid email or password.",
            "error"
        )


    return render_template(
        "login.html"
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route(
    "/logout"
)
def logout():

    session.clear()

    return redirect(
        url_for(
            "login"
        )
    )






@app.route("/glucose")
@login_required
@onboarding_required
def glucose(): return render_template("glucose.html", user=get_current_user())

@app.route("/ai-forecast")
@login_required
@onboarding_required
def ai_forecast(): return render_template("ai_forecast.html", user=get_current_user())

@app.route("/risk-trends")
@login_required
@onboarding_required
def risk_trends(): return render_template("risk_trends.html", user=get_current_user())

@app.route("/simulator")
@login_required
@onboarding_required
def simulator(): return render_template("simulator.html", user=get_current_user())

@app.route("/mental-wellness")
@login_required
@onboarding_required
def mental_wellness(): return render_template("mental_wellness.html", user=get_current_user())

@app.route("/health-trends")
@login_required
@onboarding_required
def health_trends(): return render_template("health_trends.html", user=get_current_user())


# ============================================================
# DASHBOARD
# ============================================================

@app.route(
    "/dashboard"
)
@login_required
@onboarding_required
def dashboard():

    user = get_current_user()


    records_db = (
        HealthRecord.query
        .filter_by(
            user_id=user.id
        )
        .order_by(
            HealthRecord.date.asc()
        )
        .all()
    )


    records = [

        serialize_record(
            record
        )

        for record
        in records_db

    ]


    latest_record = (

        records_db[-1]

        if records_db

        else None

    )


    health_intelligence = (
        calculate_health_intelligence(
            latest_record
        )
    )


    diet_recommendations = (
        get_diet_recommendations(
            user
        )
    )


    workout_recommendations = (
        get_workout_recommendations(
            user
        )
    )


    trend_summary = (
        calculate_trend_summary(
            records_db
        )
    )


    return render_template(

        "dashboard.html",

        user=user,

        records=records,

        latest_record=
            latest_record,

        health_intelligence=
            health_intelligence,

        diet_recommendations=
            diet_recommendations,

        workout_recommendations=
            workout_recommendations,

        trend_summary=
            trend_summary

    )


# ============================================================
# MONITORING
# ============================================================

@app.route(
    "/monitoring"
)
@login_required
@onboarding_required
def monitoring():

    user = get_current_user()


    records_db = (
        HealthRecord.query
        .filter_by(
            user_id=user.id
        )
        .order_by(
            HealthRecord.date.asc()
        )
        .all()
    )


    records = [

        serialize_record(
            record
        )

        for record
        in records_db

    ]


    latest_record = (

        records_db[-1]

        if records_db

        else None

    )


    health_intelligence = (
        calculate_health_intelligence(
            latest_record
        )
    )


    trend_summary = (
        calculate_trend_summary(
            records_db
        )
    )


    return render_template(

        "monitoring.html",

        user=user,

        records=records,

        latest_record=
            latest_record,

        health_intelligence=
            health_intelligence,

        trend_summary=
            trend_summary

    )


# ============================================================
# ADD HEALTH RECORD
# ============================================================

@app.route("/add_health", methods=["POST"])
@app.route("/add-health", methods=["POST"])
@app.route("/add_record", methods=["POST"])
@login_required
def add_health():
    user = get_current_user()

    glucose = safe_float(request.form.get("glucose"))
    stress = safe_float(request.form.get("stress"))
    sleep = safe_float(request.form.get("sleep"))
    steps = safe_int(request.form.get("steps"))
    weight = safe_float(request.form.get("weight"))
    mood = clean_text(request.form.get("mood"))
    raw_context = clean_text(request.form.get("meal_context"))
    context_map = {
        "fasting": "Fasting",
        "pre-meal": "Pre-meal",
        "pre_meal": "Pre-meal",
        "post-meal (1h)": "Post-meal (1h)",
        "post_meal_1h": "Post-meal (1h)",
        "post-meal (2h)": "Post-meal (2h)",
        "post_meal_2h": "Post-meal (2h)",
        "bedtime": "Bedtime",
        "random": "Random"
    }
    meal_context = context_map.get(raw_context.lower() if raw_context else "", raw_context)
    valid_contexts = ["Fasting", "Pre-meal", "Post-meal (1h)", "Post-meal (2h)", "Bedtime", "Random"]

    exercise_duration = safe_float(request.form.get("exercise_duration"))

    val_errors = validate_health_values(
        glucose=glucose,
        stress=stress,
        sleep=sleep,
        steps=steps,
        exercise_duration=exercise_duration,
        weight=weight
    )

    if not meal_context or meal_context not in valid_contexts:
        val_errors.append("Please select a valid Measurement context.")

    if val_errors:
        for err in val_errors:
            flash(err, "error")
        return redirect(url_for("monitoring"))

    record = HealthRecord(
        user_id=user.id,
        date=datetime.utcnow(),
        glucose=glucose,
        stress=stress,
        sleep=sleep,
        steps=steps,
        weight=weight,
        mood=mood,
        meal_context=meal_context,
        exercise_duration=exercise_duration,
        is_valid=True,
        validation_notes="Valid"
    )

    db.session.add(record)
    db.session.commit()

    flash("Health check-in saved successfully.", "success")
    return redirect(url_for("dashboard"))


# ============================================================
# NUTRITION
# ============================================================

@app.route(
    "/nutrition"
)
@login_required
@onboarding_required
def nutrition():

    user = get_current_user()


    recommendations = (
        get_diet_recommendations(
            user
        )
    )


    # ========================================================
    # IMPORTANT FIX
    #
    # The previous version created:
    #
    # meals["Breakfast"] = [item1, item2]
    #
    # but the new HTML expects:
    #
    # meals["Breakfast"] = {
    #     "foods": [...]
    # }
    #
    # This function now creates exactly that structure.
    # ========================================================

    meals = build_meal_plan(
        recommendations
    )


    meals = enrich_meal_plan(
        meals
    )


    # --------------------------------------------------------
    # Compatibility lookup
    # --------------------------------------------------------

    meal_lookup = {

        "breakfast":
            meals.get(
                "Breakfast",
                {}
            ),

        "lunch":
            meals.get(
                "Lunch",
                {}
            ),

        "snack":
            meals.get(
                "Snack",
                {}
            ),

        "dinner":
            meals.get(
                "Dinner",
                {}
            )

    }


    # --------------------------------------------------------
    # Nutrition summary
    # --------------------------------------------------------

    nutrition_totals = {

        "calories": 0,

        "carbs": 0,

        "protein": 0,

        "fiber": 0,

        "fat": 0

    }


    for item in recommendations:

        for key, field in [

            (
                "calories",
                "calories"
            ),

            (
                "carbs",
                "carbs"
            ),

            (
                "protein",
                "protein"
            ),

            (
                "fiber",
                "fiber"
            ),

            (
                "fat",
                "fat"
            )

        ]:

            value = safe_float(
                item.get(
                    field
                )
            )

            if value is not None:

                nutrition_totals[
                    key
                ] += value


    # --------------------------------------------------------
    # Advanced object expected by HTML
    # --------------------------------------------------------

    nutrition_plan = {

        "recommendations":
            recommendations,

        "meals":
            meals,

        "totals":
            nutrition_totals,

        "profile": {

            "diabetes_type":
                user.diabetes_type
                or "Not specified",

            "activity_level":
                user.activity_level
                or "Moderate",

            "goal":
                user.goal
                or "General wellness"

        }

    }


    return render_template(

        "nutrition.html",

        user=user,

        recommendations=
            recommendations,

        meals=
            meals,

        meal_lookup=
            meal_lookup,

        nutrition_plan=
            nutrition_plan

    )


# ============================================================
# WORKOUTS
# ============================================================

@app.route(
    "/workouts"
)
@login_required
@onboarding_required
def workouts():

    user = get_current_user()


    recommendations = (
        get_workout_recommendations(
            user
        )
    )


    categories = {}


    for item in recommendations:

        category = (
            clean_text(
                item.get(
                    "category"
                )
            )
            or
            "General"
        )


        if category not in categories:

            categories[
                category
            ] = []


        categories[
            category
        ].append(
            item
        )


    aerobic = [

        item

        for item
        in recommendations

        if clean_text(
            item.get(
                "category"
            )
        ).lower()
        == "aerobic"

    ]


    resistance = [

        item

        for item
        in recommendations

        if clean_text(
            item.get(
                "category"
            )
        ).lower()
        == "resistance"

    ]


    flexibility = [

        item

        for item
        in recommendations

        if clean_text(
            item.get(
                "category"
            )
        ).lower()
        in (
            "flexibility",
            "mobility"
        )

    ]


    strength = [

        item

        for item
        in recommendations

        if clean_text(
            item.get(
                "category"
            )
        ).lower()
        in (
            "strength",
            "resistance"
        )

    ]


    # General educational target.
    # It is not a personalized medical prescription.

    weekly_target = 150


    return render_template(

        "workouts.html",

        user=user,

        recommendations=
            recommendations,

        categories=
            categories,

        aerobic=
            aerobic,

        resistance=
            resistance,

        flexibility=
            flexibility,

        strength=
            strength,

        weekly_target=
            weekly_target

    )


# ============================================================
# PROFILE
# ============================================================

@app.route(
    "/profile",
    methods=[
        "GET",
        "POST"
    ]
)
@login_required
def profile():

    user = get_current_user()


    if request.method == "POST":

        name = clean_text(
            request.form.get(
                "name"
            )
        )

        if name:

            user.name = name


        diabetes_type = clean_text(
            request.form.get(
                "diabetes_type"
            )
        )

        if diabetes_type:

            user.diabetes_type = (
                diabetes_type
            )


        activity_level = clean_text(
            request.form.get(
                "activity_level"
            )
        )

        if activity_level:

            user.activity_level = (
                activity_level
            )


        goal = clean_text(
            request.form.get(
                "goal"
            )
        )

        if goal:

            user.goal = goal


        age = safe_int(
            request.form.get(
                "age"
            )
        )

        if age is not None:

            user.age = age


        height = safe_float(
            request.form.get(
                "height"
            )
        )

        if height is not None:

            user.height = height


        weight = safe_float(
            request.form.get(
                "weight"
            )
        )

        if weight is not None:

            user.weight = weight


        db.session.commit()


        flash(
            "Health profile updated.",
            "success"
        )


        return redirect(
            url_for(
                "profile"
            )
        )


    bmi = None


    if (
        user.height
        and user.weight
    ):

        height_m = (
            user.height / 100
        )


        if height_m > 0:

            bmi = round(
                user.weight
                /
                (
                    height_m
                    **
                    2
                ),
                1
            )


    return render_template(

        "profile.html",

        user=user,

        bmi=bmi

    )


# ============================================================
# HOSPITALS
# ============================================================

@app.route(
    "/hospitals"
)
@login_required
def hospitals():

    return render_template(

        "hospitals.html",

        user=
            get_current_user()

    )


# ============================================================
# EMERGENCY
# ============================================================

@app.route(
    "/emergency"
)
@login_required
def emergency():

    return render_template(

        "emergency.html",

        user=
            get_current_user()

    )


# ============================================================
# HEALTH DATA API
# ============================================================

@app.route(
    "/api/health-data"
)
@login_required
def health_data_api():

    user = get_current_user()


    records_db = (
        HealthRecord.query
        .filter_by(
            user_id=user.id
        )
        .order_by(
            HealthRecord.date.asc()
        )
        .all()
    )


    return jsonify([

        serialize_record(
            record
        )

        for record
        in records_db

    ])


# ============================================================
# HEALTH SCORE API
# ============================================================

@app.route(
    "/api/health-score"
)
@login_required
def health_score_api():

    user = get_current_user()


    latest_record = (
        HealthRecord.query
        .filter_by(
            user_id=user.id
        )
        .order_by(
            HealthRecord.date.desc()
        )
        .first()
    )


    return jsonify(
        calculate_health_intelligence(
            latest_record
        )
    )


# ============================================================
# NUTRITION API
# ============================================================

@app.route(
    "/api/nutrition"
)
@login_required
def nutrition_api():

    user = get_current_user()


    recommendations = (
        get_diet_recommendations(
            user
        )
    )


    meals = build_meal_plan(
        recommendations
    )


    meals = enrich_meal_plan(
        meals
    )


    return jsonify({

        "status":
            "success",

        "diabetes_type":
            user.diabetes_type,

        "meals":
            meals,

        "recommendations":
            recommendations

    })


# ============================================================
# WORKOUT API
# ============================================================

@app.route(
    "/api/workouts"
)
@login_required
def workouts_api():

    user = get_current_user()


    recommendations = (
        get_workout_recommendations(
            user
        )
    )


    return jsonify({

        "status":
            "success",

        "diabetes_type":
            user.diabetes_type,

        "weekly_target":
            150,

        "recommendations":
            recommendations

    })


# ============================================================
# TREND API
# ============================================================

@app.route(
    "/api/trends"
)
@login_required
def trends_api():

    user = get_current_user()


    records = (
        HealthRecord.query
        .filter_by(
            user_id=user.id
        )
        .order_by(
            HealthRecord.date.asc()
        )
        .all()
    )


    return jsonify({

        "status":
            "success",

        "summary":
            calculate_trend_summary(
                records
            ),

        "records": [

            serialize_record(
                record
            )

            for record
            in records

        ]

    })


# ============================================================
# APPLICATION STATUS
# ============================================================

@app.route(
    "/api/status"
)
def api_status():

    diet_path = os.path.join(
        DATA_DIR,
        "diet.csv"
    )

    workout_path = os.path.join(
        DATA_DIR,
        "workout.csv"
    )

    diabetes_path = os.path.join(
        DATA_DIR,
        "diabetes.csv"
    )


    return jsonify({

        "application":
            "Smart Diabetes & Mental Health Monitoring System",

        "status":
            "running",

        "database":
            "connected",

        "datasets": {

            "diabetes":
                os.path.exists(
                    diabetes_path
                ),

            "diet":
                os.path.exists(
                    diet_path
                ),

            "workout":
                os.path.exists(
                    workout_path
                )

        },

        "timestamp":
            datetime.utcnow().isoformat()

    })


# ============================================================
# ERROR HANDLER — 404
# ============================================================

@app.errorhandler(404)
def page_not_found(error):

    if request.path.startswith(
        "/api/"
    ):

        return jsonify({

            "status":
                "error",

            "message":
                "API endpoint not found",

            "path":
                request.path

        }), 404


    return render_template(
        "login.html"
    ), 404


# ============================================================
# ERROR HANDLER — 500
# ============================================================

@app.errorhandler(500)
def internal_error(error):

    db.session.rollback()


    if request.path.startswith(
        "/api/"
    ):

        return jsonify({

            "status":
                "error",

            "message":
                "Internal server error"

        }), 500


    return """

    <div style="
        font-family:Arial;
        padding:40px;
        background:#07110f;
        color:white;
        min-height:100vh;
    ">

        <h1 style="color:#ff6675;">
            Smart Health Error
        </h1>

        <p>
            Something went wrong while processing
            this request.
        </p>

        <p>
            Check the Flask terminal for the
            detailed error message.
        </p>

    </div>

    """, 500


# ============================================================
# START APPLICATION
# ============================================================


# ============================================================
# NEW UI DATA APIs (PHASE 1C)
# ============================================================
from datetime import timedelta

@app.route("/api/glucose/history")
@login_required
def api_glucose_history():
    user = get_current_user()
    try:
        days = int(request.args.get('days', 7))
        if days <= 0 or days > 365:
            days = 7
    except ValueError:
        days = 7

    cutoff = datetime.utcnow() - timedelta(days=days)
    records = HealthRecord.query.filter(
        HealthRecord.user_id == user.id, HealthRecord.is_valid == True,
        HealthRecord.date >= cutoff
    ).order_by(HealthRecord.date.asc()).all()
    
    if not records:
        return jsonify({"success": True, "records": [], "message": "No health records available yet."})

    glucose_records = [r for r in records if r.glucose is not None]
    
    if not glucose_records:
        return jsonify({"success": True, "records": [], "message": "No glucose records available yet."})

    labels = [r.date.strftime("%Y-%m-%d %H:%M") for r in glucose_records]
    values = [r.glucose for r in glucose_records]
    
    stats = {}
    if glucose_records:
        stats["current"] = glucose_records[-1].glucose
        stats["average"] = round(sum(values) / len(values), 1)
        stats["highest"] = max(values)
        stats["lowest"] = min(values)

    return jsonify({
        "success": True,
        "days": days,
        "labels": labels,
        "values": values,
        "records": [{"id": r.id, "timestamp": r.date.strftime("%Y-%m-%d %H:%M"), "glucose": r.glucose} for r in glucose_records],
        "stats": stats,
        "statistics": stats
    })

@app.route("/api/glucose/trend")
@login_required
def api_glucose_trend():
    user = get_current_user()
    try:
        days = int(request.args.get('days', 7))
        if days <= 0 or days > 365:
            days = 7
    except ValueError:
        days = 7

    cutoff = datetime.utcnow() - timedelta(days=days)
    records = HealthRecord.query.filter(
        HealthRecord.user_id == user.id, HealthRecord.is_valid == True,
        HealthRecord.date >= cutoff,
        HealthRecord.glucose.isnot(None)
    ).order_by(HealthRecord.date.asc()).all()

    if not records:
        # Fallback to all valid records
        records = HealthRecord.query.filter(
            HealthRecord.user_id == user.id, HealthRecord.is_valid == True,
            HealthRecord.glucose.isnot(None)
        ).order_by(HealthRecord.date.asc()).all()

    if not records or len(records) == 0:
        return jsonify({
            "success": True,
            "status": "No data yet",
            "trend": "none",
            "direction": "none",
            "color": "#64748b",
            "description": "No valid glucose readings recorded yet.",
            "count": 0,
            "records_used": 0
        })

    if len(records) == 1:
        return jsonify({
            "success": True,
            "status": "Baseline recorded",
            "trend": "baseline",
            "direction": "none",
            "color": "#3b82f6",
            "description": "1 valid reading recorded. Add more readings to calculate glucose trajectory.",
            "count": 1,
            "records_used": 1
        })

    half = max(1, len(records) // 2)
    first_half = [r.glucose for r in records[:half]]
    second_half = [r.glucose for r in records[half:]]
    avg_first = sum(first_half) / len(first_half)
    avg_second = sum(second_half) / len(second_half)
    change = round(avg_second - avg_first, 1)

    if change > 5.0:
        status = "Increasing"
        direction = "up"
        color = "#f59e0b"
        desc = f"Glucose has increased by {abs(change):.1f} mg/dL across recent readings."
    elif change < -5.0:
        status = "Decreasing"
        direction = "down"
        color = "#10b981"
        desc = f"Glucose has decreased by {abs(change):.1f} mg/dL across recent readings."
    else:
        status = "Stable"
        direction = "stable"
        color = "#3b82f6"
        desc = "Glucose levels are relatively steady across recent readings."

    return jsonify({
        "success": True,
        "status": status,
        "trend": status.lower(),
        "direction": direction,
        "change": change,
        "difference": change,
        "color": color,
        "description": desc,
        "records_used": len(records),
        "count": len(records)
    })

@app.route("/api/wellness/history")
@login_required
def api_wellness_history():
    user = get_current_user()
    try:
        days = int(request.args.get('days', 7))
        if days <= 0 or days > 365:
            days = 7
    except ValueError:
        days = 7

    cutoff = datetime.utcnow() - timedelta(days=days)
    records = HealthRecord.query.filter(
        HealthRecord.user_id == user.id, HealthRecord.is_valid == True,
        HealthRecord.date >= cutoff
    ).order_by(HealthRecord.date.asc()).all()

    if not records:
        return jsonify({"success": True, "records": [], "message": "No wellness records available yet."})

    labels = [r.date.strftime("%Y-%m-%d %H:%M") for r in records]
    
    return jsonify({
        "success": True,
        "labels": labels,
        "stress": [r.stress for r in records],
        "sleep": [r.sleep for r in records],
        "mood": [r.mood for r in records],
        "steps": [r.steps for r in records],
        "exercise_duration": [r.exercise_duration for r in records]
    })

@app.route("/api/health-trends")
@login_required
def api_health_trends():
    user = get_current_user()
    try:
        days = int(request.args.get('days', 7))
        if days <= 0 or days > 365:
            days = 7
    except ValueError:
        days = 7

    cutoff = datetime.utcnow() - timedelta(days=days)
    records = HealthRecord.query.filter(
        HealthRecord.user_id == user.id, HealthRecord.is_valid == True,
        HealthRecord.date >= cutoff
    ).order_by(HealthRecord.date.asc()).all()

    if not records:
        latest_rec = HealthRecord.query.filter(
            HealthRecord.user_id == user.id, HealthRecord.is_valid == True
        ).order_by(HealthRecord.date.desc()).first()
        if latest_rec and latest_rec.date:
            rel_cutoff = latest_rec.date - timedelta(days=days)
            records = HealthRecord.query.filter(
                HealthRecord.user_id == user.id, HealthRecord.is_valid == True,
                HealthRecord.date >= rel_cutoff
            ).order_by(HealthRecord.date.asc()).all()

    if not records:
        records = HealthRecord.query.filter(
            HealthRecord.user_id == user.id, HealthRecord.is_valid == True
        ).order_by(HealthRecord.date.asc()).limit(50).all()

    if not records:
        return jsonify({
            "success": True, 
            "records": [], 
            "labels": [],
            "glucose": [],
            "stress": [],
            "sleep": [],
            "steps": [],
            "weight": [],
            "mood": [],
            "exercise_duration": [],
            "message": "No health trends available yet."
        })

    labels = [r.date.strftime("%Y-%m-%d %H:%M") for r in records]

    return jsonify({
        "success": True,
        "labels": labels,
        "glucose": [r.glucose for r in records],
        "stress": [r.stress for r in records],
        "sleep": [r.sleep for r in records],
        "steps": [r.steps for r in records],
        "weight": [r.weight for r in records],
        "mood": [r.mood for r in records],
        "exercise_duration": [r.exercise_duration for r in records]
    })

@app.route("/api/health-records/recent")
@login_required
def api_recent_health_records():
    user = get_current_user()
    try:
        limit = int(request.args.get('limit', 10))
        if limit <= 0 or limit > 100:
            limit = 10
    except ValueError:
        limit = 10

    records = HealthRecord.query.filter(
        HealthRecord.user_id == user.id, HealthRecord.is_valid == True
    ).order_by(HealthRecord.date.desc()).limit(limit).all()

    if not records:
        return jsonify({"success": True, "records": [], "message": "No health records available yet."})

    ret_records = []
    for r in records:
        ret_records.append({
            "id": r.id,
            "timestamp": r.date.strftime("%Y-%m-%d %H:%M:%S"),
            "glucose": r.glucose,
            "stress": r.stress,
            "sleep": r.sleep,
            "steps": r.steps,
            "weight": r.weight,
            "mood": r.mood,
            "meal_context": r.meal_context,
            "exercise_duration": r.exercise_duration
        })

    return jsonify({
        "success": True,
        "records": ret_records
    })

@app.route("/api/health/summary")
@login_required
def api_health_summary():
    user = get_current_user()
    
    # All valid records for user
    valid_records = HealthRecord.query.filter(
        HealthRecord.user_id == user.id,
        HealthRecord.is_valid == True
    ).order_by(HealthRecord.date.desc()).all()
    
    if not valid_records:
        return jsonify({"success": True, "records": [], "message": "No valid health records available yet."})
        
    latest = valid_records[0]
    prev = valid_records[1] if len(valid_records) > 1 else None
    
    # Delta
    delta = round(latest.glucose - prev.glucose, 1) if (prev and latest.glucose is not None and prev.glucose is not None) else None
    
    # Today's glucose
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_records = [r for r in valid_records if r.date and r.date >= today and r.glucose is not None]
    today_avg = round(sum([r.glucose for r in today_records]) / len(today_records), 1) if today_records else None
    
    # Weekly glucose (last 7 days or all valid records if historical)
    week_ago = datetime.utcnow() - timedelta(days=7)
    weekly_records = [r for r in valid_records if r.date and r.date >= week_ago and r.glucose is not None]
    if not weekly_records:
        weekly_records = [r for r in valid_records if r.glucose is not None]
        
    all_glucoses = [r.glucose for r in weekly_records if r.glucose is not None]
    weekly_avg = round(sum(all_glucoses) / len(all_glucoses), 1) if all_glucoses else None
    highest = max(all_glucoses) if all_glucoses else latest.glucose
    lowest = min(all_glucoses) if all_glucoses else latest.glucose
    
    all_stress = [r.stress for r in valid_records if r.stress is not None]
    stress_avg = round(sum(all_stress) / len(all_stress), 1) if all_stress else latest.stress
    
    all_sleep = [r.sleep for r in valid_records if r.sleep is not None]
    sleep_avg = round(sum(all_sleep) / len(all_sleep), 1) if all_sleep else latest.sleep

    # Dynamic Risk Indicator calculation from verified user health records
    if latest.glucose is not None:
        if latest.glucose < 70 or latest.glucose >= 180 or (latest.stress and latest.stress >= 8):
            risk_level = "Elevated Risk"
            risk_badge_class = "risk-high"
            risk_desc = f"Latest glucose {latest.glucose} mg/dL is outside target reference range (70–140 mg/dL)."
        elif latest.glucose > 140 or (latest.stress and latest.stress >= 6):
            risk_level = "Moderate Risk"
            risk_badge_class = "risk-moderate"
            risk_desc = f"Latest glucose {latest.glucose} mg/dL is mildly above target reference range (70–140 mg/dL)."
        else:
            risk_level = "Low Risk (On Track)"
            risk_badge_class = "risk-low"
            risk_desc = f"Latest glucose {latest.glucose} mg/dL is in target reference range (70–140 mg/dL)."
    else:
        risk_level = "Insufficient Data"
        risk_badge_class = "risk-moderate"
        risk_desc = "Clinical lab biomarkers and glucose readings required."

    return jsonify({
        "success": True,
        "current_glucose": latest.glucose,
        "previous_glucose": prev.glucose if prev else None,
        "glucose_delta": delta,
        "today_average_glucose": today_avg,
        "weekly_average_glucose": weekly_avg,
        "highest_recent_glucose": highest,
        "lowest_recent_glucose": lowest,
        "latest_stress": latest.stress,
        "stress_average": stress_avg,
        "latest_sleep": latest.sleep,
        "sleep_average": sleep_avg,
        "latest_steps": latest.steps,
        "latest_weight": latest.weight,
        "latest_mood": latest.mood,
        "latest_meal": latest.meal_context,
        "latest_timestamp": latest.date.strftime("%Y-%m-%d %H:%M:%S") if latest.date else None,
        "risk_level": risk_level,
        "risk_description": risk_desc,
        "risk_badge_class": risk_badge_class
    })


@app.route('/onboarding/profile', methods=['GET', 'POST'])
@login_required
def onboarding_profile():
    user = get_current_user()
    if request.method == 'POST':
        user.age = int(request.form.get('age')) if request.form.get('age') else None
        user.gender = request.form.get('gender')
        user.height = float(request.form.get('height')) if request.form.get('height') else None
        user.weight = float(request.form.get('weight')) if request.form.get('weight') else None
        user.diabetes_type = request.form.get('diabetes_type')
        user.years_since_diagnosis = int(request.form.get('years_since_diagnosis')) if request.form.get('years_since_diagnosis') else None
        user.hba1c = float(request.form.get('hba1c')) if request.form.get('hba1c') else None

        user.egfr = float(request.form.get('egfr')) if request.form.get('egfr') else None
        user.uacr = float(request.form.get('uacr')) if request.form.get('uacr') else None
        user.last_eye_exam = request.form.get('last_eye_exam') if request.form.get('last_eye_exam') else None
        user.retinopathy_status = request.form.get('retinopathy_status') if request.form.get('retinopathy_status') else None
        user.macular_edema = request.form.get('macular_edema') if request.form.get('macular_edema') else None

        user.current_medication = request.form.get('current_medication')
        user.blood_pressure = request.form.get('blood_pressure')
        user.cholesterol = float(request.form.get('cholesterol')) if request.form.get('cholesterol') else None
        user.smoking_status = request.form.get('smoking_status')
        user.activity_level = request.form.get('activity_level')
        user.typical_sleep = float(request.form.get('typical_sleep')) if request.form.get('typical_sleep') else None
        user.typical_stress = int(request.form.get('typical_stress')) if request.form.get('typical_stress') else None
        
        user.profile_completed = True
        db.session.commit()
        return redirect(url_for('onboarding_history'))
        
    return render_template('onboarding_profile.html', user=user)

@app.route('/onboarding/history', methods=['GET', 'POST'])
@login_required
def onboarding_history():
    user = get_current_user()
    if not user.profile_completed:
        return redirect(url_for('onboarding_profile'))
        
    if request.method == 'POST':
        dates = request.form.getlist('date[]')
        glucoses = request.form.getlist('glucose[]')
        stresses = request.form.getlist('stress[]')
        sleeps = request.form.getlist('sleep[]')
        steps_list = request.form.getlist('steps[]')
        weights = request.form.getlist('weight[]')
        moods = request.form.getlist('mood[]')
        meals = request.form.getlist('meal_context[]')
        exercises = request.form.getlist('exercise_duration[]')
        
        records_to_add = []
        validation_errors = []
        
        for i in range(len(dates)):
            if not dates[i] or not glucoses[i]: continue
            
            raw_g = glucoses[i]
            raw_str = stresses[i] if i < len(stresses) else None
            raw_slp = sleeps[i] if i < len(sleeps) else None
            raw_stp = steps_list[i] if i < len(steps_list) else None
            raw_ex = exercises[i] if i < len(exercises) else None
            raw_wt = weights[i] if i < len(weights) else None
            
            errs = validate_health_values(
                glucose=raw_g,
                stress=raw_str,
                sleep=raw_slp,
                steps=raw_stp,
                exercise_duration=raw_ex,
                weight=raw_wt
            )
            if errs:
                validation_errors.extend([f"Reading {i+1}: {e}" for e in errs])
                continue
                
            try:
                ts = datetime.strptime(dates[i], '%Y-%m-%dT%H:%M')
            except ValueError:
                try:
                    ts = datetime.strptime(dates[i], '%Y-%m-%d')
                except ValueError:
                    ts = datetime.utcnow()
                    
            hr = HealthRecord(
                user_id=user.id,
                date=ts,
                glucose=float(raw_g),
                stress=float(raw_str) if raw_str else 3.0,
                sleep=float(raw_slp) if raw_slp else 7.5,
                steps=int(float(raw_stp)) if raw_stp else 5000,
                weight=float(raw_wt) if raw_wt else (user.weight or 70.0),
                mood=moods[i] if i < len(moods) and moods[i] else '5',
                meal_context=meals[i] if i < len(meals) and meals[i] else 'Random',
                exercise_duration=float(raw_ex) if raw_ex else 30.0,
                is_valid=True,
                validation_notes="Valid"
            )
            records_to_add.append(hr)
            
        if validation_errors:
            for err in validation_errors:
                flash(err, "error")
            return render_template('onboarding_history.html', user=user)
            
        if len(records_to_add) < 5:
            flash("Please enter at least 5 valid health readings to establish your baseline.", "error")
            return render_template('onboarding_history.html', user=user)
            
        for r in records_to_add:
            db.session.add(r)
            
        user.onboarding_completed = True
        db.session.commit()
        return redirect(url_for('onboarding_review'))
        
    return render_template('onboarding_history.html', user=user)

@app.route('/onboarding/review')
@login_required
def onboarding_review():
    user = get_current_user()
    records_count = HealthRecord.query.filter_by(user_id=user.id).count()
    return render_template('onboarding_review.html', user=user, records_count=records_count)

@app.route('/onboarding/processing')
@login_required
def onboarding_processing():
    return render_template('onboarding_processing.html')




# ============================================================
# PHASE 2 - REAL GRU AI FORECAST & SIMULATION APIS
# ============================================================
from ai.model_service import model_service

@app.route("/api/forecast/status", methods=["GET"])
@login_required
def api_forecast_status():
    user = get_current_user()
    records = HealthRecord.query.filter_by(user_id=user.id, is_valid=True).order_by(HealthRecord.date.asc()).all()
    return jsonify(model_service.get_status(user_record_count=len(records)))

@app.route("/api/forecast/predict", methods=["POST", "GET"])
@login_required
def api_forecast_predict():
    user = get_current_user()
    records = HealthRecord.query.filter_by(user_id=user.id, is_valid=True).order_by(HealthRecord.date.asc()).all()
    result = model_service.predict_forecast(records)
    return jsonify(result)

@app.route("/api/forecast/simulate", methods=["POST"])
@login_required
def api_forecast_simulate():
    user = get_current_user()
    records = HealthRecord.query.filter_by(user_id=user.id, is_valid=True).order_by(HealthRecord.date.asc()).all()
    data = request.get_json(silent=True) or request.form
    exercise_mins = float(data.get("exercise_mins", 0))
    sleep_hours = float(data.get("sleep_hours", 7.0))
    meal_context = data.get("meal_context", "Normal")
    result = model_service.simulate_whatif(records, exercise_mins, sleep_hours, meal_context)
    return jsonify(result)




    
    if user.egfr < 60 or user.uacr > 300:
        risk = 'High'
        lvl = 'high'
        exp = 'High risk indicator per KDIGO guidelines based on low eGFR or high uACR. Risk assessment - not a diagnosis.'
    elif (60 <= user.egfr <= 89 and user.uacr > 30) or (user.egfr >= 90 and user.uacr > 30):
        risk = 'Moderate'
        lvl = 'moderate'
        exp = 'Moderate risk indicator per KDIGO guidelines due to moderately increased albuminuria. Risk assessment - not a diagnosis.'
    else:
        risk = 'Low'
        lvl = 'low'
        exp = 'Low risk indicator per KDIGO guidelines. Maintain routine screening. Risk assessment - not a diagnosis.'
        
    return jsonify({
        'status': 'success',
        'risk': risk,
        'explanation': exp,
        'inputs': f'eGFR: {user.egfr}, uACR: {user.uacr}',
        'level': lvl
    })


    
    if user.retinopathy_status in ['Severe', 'Proliferative'] or user.macular_edema == 'Present':
        risk = 'High'
        lvl = 'high'
        exp = 'High risk indicator per ADA guidelines. Requires close specialist monitoring. Risk assessment - not a diagnosis.'
    elif user.retinopathy_status in ['Mild', 'Moderate']:
        risk = 'Moderate'
        lvl = 'moderate'
        exp = 'Moderate risk indicator per ADA guidelines. Annual follow-ups recommended. Risk assessment - not a diagnosis.'
    else:
        risk = 'Low'
        lvl = 'low'
        exp = 'Low risk indicator per ADA guidelines. Continue regular eye exams. Risk assessment - not a diagnosis.'
        
    return jsonify({
        'status': 'success',
        'risk': risk,
        'explanation': exp,
        'inputs': f'Exam: {user.last_eye_exam}, Retinopathy: {user.retinopathy_status}, Edema: {user.macular_edema}',
        'level': lvl
    })



@app.route('/api/complications/kidney')
@login_required
def api_kidney():
    user = get_current_user()
    
    if user.egfr is not None and user.uacr is not None:
        inputs = f'eGFR: {user.egfr} • uACR: {user.uacr}'
        if user.egfr < 60 or user.uacr > 300:
            return jsonify({'status': 'success', 'risk': 'HIGH', 'level': 'high', 'inputs': inputs, 'explanation': 'High risk indicator per KDIGO guidelines based on low eGFR or high uACR. Clinical evaluation is recommended.'})
        elif (60 <= user.egfr <= 89 and user.uacr > 30) or (user.egfr >= 90 and user.uacr > 30):
            return jsonify({'status': 'success', 'risk': 'MODERATE', 'level': 'moderate', 'inputs': inputs, 'explanation': 'Moderate risk indicator per KDIGO guidelines due to moderately increased albuminuria. Additional clinical monitoring is recommended.'})
        else:
            return jsonify({'status': 'success', 'risk': 'LOW', 'level': 'low', 'inputs': inputs, 'explanation': 'Low risk indicator per KDIGO guidelines. Current available factors do not indicate an elevated complication risk. Continue routine monitoring.'})
            
    factors_used = []
    risk_points = 0
    
    if user.hba1c:
        factors_used.append('HbA1c')
        if user.hba1c > 9.0: risk_points += 2
        elif user.hba1c > 7.5: risk_points += 1
        
    if user.years_since_diagnosis:
        factors_used.append('Diabetes duration')
        if user.years_since_diagnosis > 10: risk_points += 2
        elif user.years_since_diagnosis > 5: risk_points += 1
        
    if user.blood_pressure:
        factors_used.append('Blood pressure')
        try:
            sys, dia = map(int, user.blood_pressure.split('/'))
            if sys >= 160 or dia >= 100: risk_points += 2
            elif sys >= 140 or dia >= 90: risk_points += 1
        except:
            pass

    if user.age:
        factors_used.append('Age')
        if user.age > 60: risk_points += 1

    if not factors_used:
        return jsonify({
            'status': 'success',
            'risk': 'INSUFFICIENT DATA',
            'level': 'missing',
            'explanation': 'More clinical information is required for a meaningful risk assessment.',
            'inputs': 'Missing'
        })
        
    inputs_str = ' • '.join(factors_used)
    
    if risk_points >= 3:
        return jsonify({'status': 'success', 'risk': 'HIGH', 'level': 'high', 'inputs': inputs_str, 'explanation': 'Multiple available factors indicate elevated future complication risk. Clinical evaluation is recommended.'})
    elif risk_points >= 1:
        return jsonify({'status': 'success', 'risk': 'MODERATE', 'level': 'moderate', 'inputs': inputs_str, 'explanation': 'Some available diabetes-related factors indicate increased future risk. Additional clinical monitoring is recommended.'})
    else:
        return jsonify({'status': 'success', 'risk': 'LOW', 'level': 'low', 'inputs': inputs_str, 'explanation': 'Current available factors do not indicate an elevated complication risk. Continue routine monitoring.'})

@app.route('/api/complications/eye')
@login_required
def api_eye():
    user = get_current_user()
    
    if user.retinopathy_status and user.macular_edema:
        inputs = f'Retinopathy: {user.retinopathy_status} • Edema: {user.macular_edema}'
        if user.retinopathy_status in ['Severe', 'Proliferative'] or user.macular_edema == 'Present':
            return jsonify({'status': 'success', 'risk': 'HIGH', 'level': 'high', 'inputs': inputs, 'explanation': 'High risk indicator per ADA guidelines. Clinical evaluation is recommended.'})
        elif user.retinopathy_status in ['Mild', 'Moderate']:
            return jsonify({'status': 'success', 'risk': 'MODERATE', 'level': 'moderate', 'inputs': inputs, 'explanation': 'Moderate risk indicator per ADA guidelines. Additional clinical monitoring is recommended.'})
        elif user.retinopathy_status == 'None' and user.macular_edema == 'Absent':
            return jsonify({'status': 'success', 'risk': 'LOW', 'level': 'low', 'inputs': inputs, 'explanation': 'Low risk indicator per ADA guidelines. Current available factors do not indicate an elevated complication risk. Continue routine monitoring.'})
            
    factors_used = []
    risk_points = 0
    
    if user.hba1c:
        factors_used.append('HbA1c')
        if user.hba1c > 9.0: risk_points += 2
        elif user.hba1c > 7.5: risk_points += 1
        
    if user.years_since_diagnosis:
        factors_used.append('Diabetes duration')
        if user.years_since_diagnosis > 15: risk_points += 2
        elif user.years_since_diagnosis > 5: risk_points += 1
        
    if user.age:
        factors_used.append('Age')
        if user.age > 65: risk_points += 1

    if not factors_used:
        return jsonify({
            'status': 'success',
            'risk': 'INSUFFICIENT DATA',
            'level': 'missing',
            'explanation': 'More clinical information is required for a meaningful risk assessment.',
            'inputs': 'Missing'
        })
        
    inputs_str = ' • '.join(factors_used)
    
    if risk_points >= 3:
        return jsonify({'status': 'success', 'risk': 'HIGH', 'level': 'high', 'inputs': inputs_str, 'explanation': 'Multiple available factors indicate elevated future complication risk. Clinical evaluation is recommended.'})
    elif risk_points >= 1:
        return jsonify({'status': 'success', 'risk': 'MODERATE', 'level': 'moderate', 'inputs': inputs_str, 'explanation': 'Some available diabetes-related factors indicate increased future risk. Additional clinical monitoring is recommended.'})
    else:
        return jsonify({'status': 'success', 'risk': 'LOW', 'level': 'low', 'inputs': inputs_str, 'explanation': 'Current available factors do not indicate an elevated complication risk. Continue routine monitoring.'})


@app.route('/api/complications/cardiovascular')
@login_required
def api_cardiovascular():
    user = get_current_user()
    factors = []
    risk_points = 0
    
    if user.age:
        factors.append('Age')
        if user.age > 50: risk_points += 1
    if user.blood_pressure:
        factors.append('BP')
        try:
            sys, dia = map(int, user.blood_pressure.split('/'))
            if sys >= 140 or dia >= 90: risk_points += 2
        except: pass
    if user.cholesterol:
        factors.append('Cholesterol')
        if user.cholesterol > 200: risk_points += 1
    if user.hba1c:
        factors.append('HbA1c')
        if user.hba1c > 8.0: risk_points += 1
    if user.smoking_status and user.smoking_status.lower() in ['yes', 'former', 'current']:
        factors.append('Smoking')
        if user.smoking_status.lower() in ['yes', 'current']: risk_points += 2
        
    if not factors:
        return jsonify({
            'status': 'success',
            'risk': 'INSUFFICIENT DATA',
            'level': 'missing',
            'inputs': 'Missing',
            'explanation': 'More clinical information is required for a meaningful risk assessment.'
        })
        
    if risk_points >= 3:
        risk = 'HIGH'
        lvl = 'high'
        exp = 'Multiple available factors indicate elevated future cardiovascular risk. Clinical evaluation is recommended.'
    elif risk_points >= 1:
        risk = 'MODERATE'
        lvl = 'moderate'
        exp = 'Some available factors indicate increased future risk. Additional clinical monitoring is recommended.'
    else:
        risk = 'LOW'
        lvl = 'low'
        exp = 'Current available factors do not indicate an elevated complication risk. Continue routine monitoring.'
        
    return jsonify({
        'status': 'success',
        'risk': risk,
        'level': lvl,
        'inputs': ' • '.join(factors),
        'explanation': exp
    })

@app.route('/api/mental-wellness')
@login_required
def api_mental_wellness():
    user = get_current_user()
    records = HealthRecord.query.filter_by(user_id=user.id).order_by(HealthRecord.date.desc()).limit(7).all()
    records = records[::-1] # chronological
    
    labels = []
    stress = []
    sleep = []
    
    for r in records:
        labels.append(r.date.strftime('%m-%d'))
        stress.append(r.stress if r.stress else 0)
        sleep.append(r.sleep if r.sleep else 0)
        
    avg_stress = sum(stress)/len(stress) if stress else 0
    avg_sleep = sum(sleep)/len(sleep) if sleep else 0
    
    return jsonify({
        'status': 'success',
        'labels': labels,
        'stress': stress,
        'sleep': sleep,
        'avg_stress': round(avg_stress, 1),
        'avg_sleep': round(avg_sleep, 1)
    })


@app.route('/risk-analysis')
@login_required
def risk_analysis():
    return render_template('risk_analysis.html', user=get_current_user())

if __name__ == "__main__":

    print()
    print("=" * 70)

    print(
        "SMART DIABETES & MENTAL HEALTH MONITORING SYSTEM"
    )

    print("=" * 70)

    print(
        "Database:",
        DATABASE_PATH
    )

    print(
        "Data folder:",
        DATA_DIR
    )

    print()

    print(
        "Dashboard : http://127.0.0.1:5000/dashboard"
    )

    print(
        "Monitoring: http://127.0.0.1:5000/monitoring"
    )

    print(
        "Nutrition : http://127.0.0.1:5000/nutrition"
    )

    print(
        "Workouts  : http://127.0.0.1:5000/workouts"
    )

    print(
        "Status    : http://127.0.0.1:5000/api/status"
    )

    print(
        "Intelligence: http://127.0.0.1:5000/api/intelligence"
    )

    print(
        "Patterns : http://127.0.0.1:5000/api/patterns"
    )

    print(
        "Anomalies: http://127.0.0.1:5000/api/anomalies"
    )

    print(
        "Nutrition AI: http://127.0.0.1:5000/api/nutrition-intelligence"
    )

    print(
        "Workout AI: http://127.0.0.1:5000/api/workout-intelligence"
    )

    print("=" * 70)

    print()


    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(
        debug=False,
        use_reloader=False,
        threaded=True,
        host="0.0.0.0",
        port=port
    )

