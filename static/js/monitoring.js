/* ============================================================
   DiaMind AI — Monitoring Intelligence
   ============================================================ */

let diaMindData = null;

document.addEventListener("DOMContentLoaded", () => {
    initializeMonitoring();
});

async function initializeMonitoring() {
    try {
        showMonitoringLoading();

        const response = await fetch("/api/intelligence?days=90");

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        diaMindData = await response.json();

        window.diaMindIntelligence = diaMindData;

        updateHealthScore();
        updateGlucoseMetrics();
        updateWellnessMetrics();
        updateActivityMetrics();
        updateNutritionMetrics();
        updateAlerts();
        updateInsights();
        updatePatterns();
        updateDataQuality();

        await loadMonitoringCharts();

        hideMonitoringLoading();

    } catch (error) {
        console.error("DiaMind Monitoring Error:", error);
        showMonitoringError();
    }
}


/* ============================================================
   HEALTH SCORE
   ============================================================ */

function updateHealthScore() {

    const scoreElement =
        document.querySelector("[data-health-score]");

    const statusElement =
        document.querySelector("[data-health-status]");

    if (!diaMindData?.overall) return;

    const score =
        diaMindData.overall.score ?? 0;

    if (scoreElement) {
        animateNumber(
            scoreElement,
            0,
            score,
            900
        );
    }

    if (statusElement) {
        statusElement.textContent =
            diaMindData.overall.status || "Collecting data";
    }

    updateScoreRing(score);
}


function updateScoreRing(score) {

    const ring =
        document.querySelector("[data-score-ring]");

    if (!ring) return;

    const circumference = 440;

    const progress =
        circumference -
        (score / 100) * circumference;

    ring.style.strokeDashoffset =
        progress;
}


/* ============================================================
   GLUCOSE
   ============================================================ */

function updateGlucoseMetrics() {

    const glucose =
        diaMindData?.glucose;

    if (!glucose) return;

    setText(
        "[data-glucose-latest]",
        formatValue(glucose.latest, " mg/dL")
    );

    setText(
        "[data-glucose-average]",
        formatValue(glucose.average, " mg/dL")
    );

    setText(
        "[data-glucose-min]",
        formatValue(glucose.minimum, " mg/dL")
    );

    setText(
        "[data-glucose-max]",
        formatValue(glucose.maximum, " mg/dL")
    );

    setText(
        "[data-glucose-trend]",
        glucose.trend || "--"
    );

    setText(
        "[data-glucose-variability]",
        formatValue(glucose.variability, "%")
    );

    setText(
        "[data-glucose-baseline]",
        formatValue(glucose.baseline, " mg/dL")
    );

    setText(
        "[data-glucose-consistency]",
        formatValue(glucose.consistency, "%")
    );

    updateTrendIndicator(
        "[data-glucose-trend-indicator]",
        glucose.trend
    );
}


/* ============================================================
   WELLNESS
   ============================================================ */

function updateWellnessMetrics() {

    const wellness =
        diaMindData?.wellness;

    if (!wellness) return;

    const stress =
        wellness.stress || {};

    const sleep =
        wellness.sleep || {};

    setText(
        "[data-stress-score]",
        formatValue(
            stress.latest,
            ""
        )
    );

    setText(
        "[data-stress-status]",
        stress.status || "--"
    );

    setText(
        "[data-sleep-hours]",
        formatValue(
            sleep.latest,
            " hrs"
        )
    );

    setText(
        "[data-sleep-status]",
        sleep.status || "--"
    );

    setText(
        "[data-recovery-score]",
        formatValue(
            wellness.recovery_score,
            "/100"
        )
    );

    setText(
        "[data-mood]",
        wellness.mood?.latest || "--"
    );
}


/* ============================================================
   ACTIVITY
   ============================================================ */

function updateActivityMetrics() {

    const activity =
        diaMindData?.activity;

    if (!activity) return;

    const steps =
        activity.steps || {};

    const exercise =
        activity.exercise || {};

    setText(
        "[data-steps]",
        formatNumber(
            steps.latest
        )
    );

    setText(
        "[data-average-steps]",
        formatNumber(
            steps.average
        )
    );

    setText(
        "[data-activity-status]",
        steps.status || "--"
    );

    setText(
        "[data-exercise-minutes]",
        formatValue(
            exercise.total,
            " min"
        )
    );

    setText(
        "[data-active-days]",
        exercise.active_days ?? "--"
    );
}


/* ============================================================
   NUTRITION
   ============================================================ */

function updateNutritionMetrics() {

    const nutrition =
        diaMindData?.nutrition;

    if (!nutrition) return;

    setText(
        "[data-nutrition-score]",
        formatValue(
            nutrition.score,
            "/100"
        )
    );

    setText(
        "[data-average-calories]",
        formatNumber(
            nutrition.average_calories
        )
    );

    setText(
        "[data-average-carbs]",
        formatValue(
            nutrition.average_carbs,
            " g"
        )
    );

    setText(
        "[data-average-protein]",
        formatValue(
            nutrition.average_protein,
            " g"
        )
    );

    setText(
        "[data-average-fiber]",
        formatValue(
            nutrition.average_fiber,
            " g"
        )
    );

    setText(
        "[data-meal-count]",
        nutrition.meal_count ?? 0
    );
}


/* ============================================================
   ALERTS
   ============================================================ */

function updateAlerts() {

    const container =
        document.querySelector(
            "[data-health-alerts]"
        );

    if (!container) return;

    const alerts =
        diaMindData?.alerts || [];

    if (!alerts.length) {

        container.innerHTML = `
            <div class="monitor-empty-state">
                <div class="empty-icon">✓</div>
                <strong>No current alerts</strong>
                <p>
                    Keep logging your health data consistently.
                </p>
            </div>
        `;

        return;
    }

    container.innerHTML =
        alerts.map(alert => `

            <div class="health-alert ${escapeHtml(
                alert.severity || "medium"
            )}">

                <div class="alert-icon">
                    ${alert.severity === "high" ? "!" : "⚠"}
                </div>

                <div class="alert-content">

                    <strong>
                        ${escapeHtml(
                            alert.title || "Health alert"
                        )}
                    </strong>

                    <p>
                        ${escapeHtml(
                            alert.message || ""
                        )}
                    </p>

                </div>

            </div>

        `).join("");
}


/* ============================================================
   AI INSIGHTS
   ============================================================ */

function updateInsights() {

    const container =
        document.querySelector(
            "[data-ai-insights]"
        );

    if (!container) return;

    const insights =
        diaMindData?.insights || [];

    if (!insights.length) {

        container.innerHTML =
            `<p>No insights available yet.</p>`;

        return;
    }

    container.innerHTML =
        insights.map(insight => `

            <div class="ai-insight-card">

                <span class="insight-category">
                    ${escapeHtml(
                        insight.category || "AI"
                    )}
                </span>

                <h4>
                    ${escapeHtml(
                        insight.title || ""
                    )}
                </h4>

                <p>
                    ${escapeHtml(
                        insight.message || ""
                    )}
                </p>

            </div>

        `).join("");
}


/* ============================================================
   PATTERNS
   ============================================================ */

function updatePatterns() {

    const container =
        document.querySelector(
            "[data-ai-patterns]"
        );

    if (!container) return;

    const patterns =
        diaMindData?.patterns || [];

    if (!patterns.length) {

        container.innerHTML = `
            <div class="monitor-empty-state">
                <strong>Collecting personal patterns</strong>
                <p>
                    More consistent data will allow DiaMind AI
                    to identify relationships.
                </p>
            </div>
        `;

        return;
    }

    container.innerHTML =
        patterns.map(pattern => `

            <div class="pattern-card">

                <div class="pattern-title">
                    ${escapeHtml(
                        pattern.name
                    )}
                </div>

                <div class="pattern-value">
                    ${pattern.correlation ?? "--"}
                </div>

                <div class="pattern-strength">
                    ${escapeHtml(
                        pattern.strength || "Unknown"
                    )}
                </div>

            </div>

        `).join("");
}


/* ============================================================
   ANOMALIES
   ============================================================ */

function updateDataQuality() {

    const element =
        document.querySelector(
            "[data-data-quality]"
        );

    if (!element) return;

    const quality =
        diaMindData?.data_quality ?? 0;

    element.textContent =
        `${quality}%`;

    const bar =
        document.querySelector(
            "[data-data-quality-bar]"
        );

    if (bar) {

        bar.style.width =
            `${quality}%`;

    }
}


/* ============================================================
   CHARTS
   ============================================================ */

async function loadMonitoringCharts() {

    if (
        typeof createGlucoseChart !==
        "function"
    ) {
        return;
    }

    try {

        const response =
            await fetch(
                "/api/monitoring"
            );

        if (!response.ok) return;

        const result =
            await response.json();

        const records =
            result.records || [];

        createGlucoseChart(
            "glucoseChart",
            records
        );

        if (
            typeof createWellnessChart ===
            "function"
        ) {
            createWellnessChart(
                "wellnessChart",
                records
            );
        }

        if (
            typeof createActivityChart ===
            "function"
        ) {
            createActivityChart(
                "activityChart",
                records
            );
        }

    } catch (error) {

        console.error(
            "Chart loading error:",
            error
        );
    }
}


/* ============================================================
   LOADING / ERROR
   ============================================================ */

function showMonitoringLoading() {

    document
        .querySelectorAll(
            "[data-monitoring-loading]"
        )
        .forEach(element => {

            element.style.display =
                "block";

        });
}


function hideMonitoringLoading() {

    document
        .querySelectorAll(
            "[data-monitoring-loading]"
        )
        .forEach(element => {

            element.style.display =
                "none";

        });
}


function showMonitoringError() {

    hideMonitoringLoading();

    const container =
        document.querySelector(
            "[data-monitoring-error]"
        );

    if (container) {

        container.style.display =
            "block";

    }
}


/* ============================================================
   UTILITIES
   ============================================================ */

function setText(
    selector,
    value
) {

    const element =
        document.querySelector(
            selector
        );

    if (element) {

        element.textContent =
            value ?? "--";

    }
}


function formatValue(
    value,
    suffix = ""
) {

    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {

        return "--";

    }

    return `${value}${suffix}`;
}


function formatNumber(value) {

    if (
        value === null ||
        value === undefined
    ) {

        return "--";

    }

    return Number(
        value
    ).toLocaleString(
        "en-IN"
    );
}


function updateTrendIndicator(
    selector,
    trend
) {

    const element =
        document.querySelector(
            selector
        );

    if (!element) return;

    element.classList.remove(
        "trend-up",
        "trend-down",
        "trend-stable"
    );

    if (trend === "Rising") {

        element.classList.add(
            "trend-up"
        );

        element.textContent =
            "↑ Rising";

    } else if (
        trend === "Falling"
    ) {

        element.classList.add(
            "trend-down"
        );

        element.textContent =
            "↓ Falling";

    } else {

        element.classList.add(
            "trend-stable"
        );

        element.textContent =
            "→ Stable";

    }
}


function animateNumber(
    element,
    start,
    end,
    duration
) {

    const startTime =
        performance.now();

    function update(time) {

        const progress =
            Math.min(
                (time - startTime)
                /
                duration,
                1
            );

        const value =
            Math.round(
                start +
                (end - start) *
                progress
            );

        element.textContent =
            value;

        if (progress < 1) {

            requestAnimationFrame(
                update
            );

        }

    }

    requestAnimationFrame(
        update
    );
}


function escapeHtml(value) {

    return String(
        value ?? ""
    )
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}