/* ============================================================
   DiaMind AI — Health Charts
   Requires Chart.js
   ============================================================ */

let glucoseChartInstance = null;
let wellnessChartInstance = null;
let activityChartInstance = null;


/* ============================================================
   GLUCOSE CHART
   ============================================================ */

function createGlucoseChart(
    canvasId,
    records
) {

    const canvas =
        document.getElementById(
            canvasId
        );

    if (!canvas) return;

    const rows =
        (records || []).filter(
            record =>
                record.glucose !== null &&
                record.glucose !== undefined
        );

    const labels =
        rows.map(
            record =>
                `${record.date} ${record.time}`
        );

    const values =
        rows.map(
            record =>
                record.glucose
        );

    if (
        glucoseChartInstance
    ) {
        glucoseChartInstance.destroy();
    }

    glucoseChartInstance =
        new Chart(
            canvas,
            {

                type: "line",

                data: {

                    labels,

                    datasets: [

                        {

                            label:
                                "Glucose",

                            data:
                                values,

                            tension:
                                0.35,

                            borderWidth:
                                3,

                            pointRadius:
                                3,

                            fill:
                                true,

                            backgroundColor:
                                "rgba(37, 99, 235, 0.08)",

                            borderColor:
                                "#2563eb"

                        }

                    ]

                },

                options: {

                    responsive:
                        true,

                    maintainAspectRatio:
                        false,

                    interaction: {

                        mode:
                            "index",

                        intersect:
                            false

                    },

                    scales: {

                        y: {

                            title: {

                                display:
                                    true,

                                text:
                                    "Glucose (mg/dL)"

                            }

                        }

                    },

                    plugins: {

                        legend: {

                            display:
                                false

                        },

                        tooltip: {

                            callbacks: {

                                label:
                                    context =>
                                        `Glucose: ${context.parsed.y} mg/dL`

                            }

                        }

                    }

                }

            }
        );
}


/* ============================================================
   WELLNESS CHART
   ============================================================ */

function createWellnessChart(
    canvasId,
    records
) {

    const canvas =
        document.getElementById(
            canvasId
        );

    if (!canvas) return;

    const rows =
        records || [];

    const labels =
        rows.map(
            r => r.date
        );

    const stress =
        rows.map(
            r =>
                r.stress
        );

    const sleep =
        rows.map(
            r =>
                r.sleep
        );

    if (
        wellnessChartInstance
    ) {

        wellnessChartInstance.destroy();

    }

    wellnessChartInstance =
        new Chart(
            canvas,
            {

                type: "line",

                data: {

                    labels,

                    datasets: [

                        {

                            label:
                                "Stress",

                            data:
                                stress,

                            tension:
                                0.35,

                            borderWidth:
                                2

                        },

                        {

                            label:
                                "Sleep",

                            data:
                                sleep,

                            tension:
                                0.35,

                            borderWidth:
                                2

                        }

                    ]

                },

                options: {

                    responsive:
                        true,

                    maintainAspectRatio:
                        false,

                    interaction: {

                        mode:
                            "index",

                        intersect:
                            false

                    }

                }

            }
        );
}


/* ============================================================
   ACTIVITY CHART
   ============================================================ */

function createActivityChart(
    canvasId,
    records
) {

    const canvas =
        document.getElementById(
            canvasId
        );

    if (!canvas) return;

    const rows =
        records || [];

    const labels =
        rows.map(
            r => r.date
        );

    const steps =
        rows.map(
            r =>
                r.steps
        );

    if (
        activityChartInstance
    ) {

        activityChartInstance.destroy();

    }

    activityChartInstance =
        new Chart(
            canvas,
            {

                type: "bar",

                data: {

                    labels,

                    datasets: [

                        {

                            label:
                                "Steps",

                            data:
                                steps,

                            borderRadius:
                                6

                        }

                    ]

                },

                options: {

                    responsive:
                        true,

                    maintainAspectRatio:
                        false,

                    plugins: {

                        legend: {

                            display:
                                false

                        }

                    }

                }

            }
        );
}