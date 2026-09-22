"""
DiaMind AI - Glucose Intelligence Engine

Responsible for:
- glucose statistics
- trends
- variability
- personal baseline
- abnormal-reading flags
- time-of-day analysis
- consistency scoring
"""

from statistics import mean
from datetime import datetime


class GlucoseEngine:

    def __init__(self, records=None):

        self.records = records or []

        self.readings = [
            r for r in self.records
            if getattr(r, "glucose", None) is not None
        ]

        self.values = [
            float(r.glucose)
            for r in self.readings
        ]


    # ---------------------------------------------------------
    # BASIC STATISTICS
    # ---------------------------------------------------------

    def average(self):

        if not self.values:
            return None

        return round(
            mean(self.values),
            1
        )


    def minimum(self):

        if not self.values:
            return None

        return round(
            min(self.values),
            1
        )


    def maximum(self):

        if not self.values:
            return None

        return round(
            max(self.values),
            1
        )


    # ---------------------------------------------------------
    # LATEST
    # ---------------------------------------------------------

    def latest(self):

        if not self.values:
            return None

        return round(
            self.values[-1],
            1
        )


    # ---------------------------------------------------------
    # TREND
    # ---------------------------------------------------------

    def trend(self):

        if len(self.values) < 3:
            return "Insufficient data"

        recent = mean(
            self.values[-3:]
        )

        previous_values = (
            self.values[:-3]
            or self.values[:1]
        )

        previous = mean(
            previous_values
        )

        difference = recent - previous

        if difference > 10:
            return "Rising"

        if difference < -10:
            return "Falling"

        return "Stable"


    # ---------------------------------------------------------
    # VARIABILITY
    # ---------------------------------------------------------

    def variability(self):

        if len(self.values) < 2:
            return None

        average = mean(
            self.values
        )

        if average == 0:
            return None

        spread = (
            max(self.values)
            -
            min(self.values)
        )

        return round(
            (spread / average) * 100,
            1
        )


    # ---------------------------------------------------------
    # BASELINE
    # ---------------------------------------------------------

    def baseline(self):

        if not self.values:
            return None

        if len(self.values) < 7:
            baseline_values = self.values
        else:
            baseline_values = self.values[-7:]

        return round(
            mean(baseline_values),
            1
        )


    # ---------------------------------------------------------
    # STATUS
    # ---------------------------------------------------------

    def status(self):

        latest = self.latest()

        if latest is None:
            return "No data"

        if latest < 70:
            return "Low"

        if latest > 180:
            return "Elevated"

        return "Within monitoring range"


    # ---------------------------------------------------------
    # ABNORMAL READINGS
    # ---------------------------------------------------------

    def abnormal_readings(self):

        low = 0
        elevated = 0

        for value in self.values:

            if value < 70:
                low += 1

            elif value > 180:
                elevated += 1

        return {
            "low": low,
            "elevated": elevated,
            "total": low + elevated
        }


    # ---------------------------------------------------------
    # CONSISTENCY
    # ---------------------------------------------------------

    def consistency_score(self):

        if len(self.values) < 3:
            return None

        variability = self.variability()

        if variability is None:
            return None

        score = 100 - variability

        return round(
            max(
                0,
                min(
                    100,
                    score
                )
            )
        )


    # ---------------------------------------------------------
    # TIME OF DAY
    # ---------------------------------------------------------

    def time_of_day(self):

        buckets = {
            "Morning": [],
            "Afternoon": [],
            "Evening": [],
            "Night": []
        }

        for record in self.readings:

            try:

                hour = record.date.hour

            except Exception:

                continue


            if 5 <= hour < 12:

                buckets["Morning"].append(
                    record.glucose
                )

            elif 12 <= hour < 17:

                buckets["Afternoon"].append(
                    record.glucose
                )

            elif 17 <= hour < 22:

                buckets["Evening"].append(
                    record.glucose
                )

            else:

                buckets["Night"].append(
                    record.glucose
                )


        result = {}

        for name, values in buckets.items():

            result[name] = (
                round(mean(values), 1)
                if values
                else None
            )

        return result


    # ---------------------------------------------------------
    # CONSECUTIVE FLAGS
    # ---------------------------------------------------------

    def consecutive_flags(self):

        low_streak = 0
        elevated_streak = 0

        max_low = 0
        max_elevated = 0

        for value in self.values:

            if value < 70:

                low_streak += 1
                elevated_streak = 0

            elif value > 180:

                elevated_streak += 1
                low_streak = 0

            else:

                low_streak = 0
                elevated_streak = 0


            max_low = max(
                max_low,
                low_streak
            )

            max_elevated = max(
                max_elevated,
                elevated_streak
            )


        return {
            "max_low_streak": max_low,
            "max_elevated_streak": max_elevated
        }


    # ---------------------------------------------------------
    # COMPLETE ANALYSIS
    # ---------------------------------------------------------

    def analyze(self):

        return {

            "latest":
                self.latest(),

            "average":
                self.average(),

            "minimum":
                self.minimum(),

            "maximum":
                self.maximum(),

            "trend":
                self.trend(),

            "variability":
                self.variability(),

            "baseline":
                self.baseline(),

            "status":
                self.status(),

            "abnormal":
                self.abnormal_readings(),

            "consistency":
                self.consistency_score(),

            "time_of_day":
                self.time_of_day(),

            "consecutive":
                self.consecutive_flags(),

            "readings":
                len(self.values)

        }