"""
DiaMind AI - Anomaly Detection Engine

This detects unusual values relative to the user's
own historical baseline.
"""


from statistics import mean


class AnomalyEngine:

    def __init__(self, records=None):

        self.records = records or []


    def detect_glucose(self):

        values = [

            r.glucose

            for r in self.records

            if getattr(
                r,
                "glucose",
                None
            ) is not None

        ]


        if len(values) < 5:

            return []


        baseline = mean(
            values[:-1]
        )

        latest = values[-1]


        if baseline == 0:

            return []


        difference = (
            latest - baseline
        )


        percentage = (
            abs(difference)
            /
            baseline
            *
            100
        )


        if percentage < 25:

            return []


        return [{

            "metric":
                "glucose",

            "latest":
                round(latest, 1),

            "baseline":
                round(baseline, 1),

            "difference":
                round(difference, 1),

            "message":
                "Your latest glucose reading differs substantially from your recent personal baseline."

        }]


    def analyze(self):

        return {

            "glucose":
                self.detect_glucose()

        }