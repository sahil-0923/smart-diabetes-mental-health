/* ============================================================
   DiaMind AI — Dashboard
   ============================================================ */

document.addEventListener(
    "DOMContentLoaded",
    () => {

        loadDashboardIntelligence();

    }
);


async function loadDashboardIntelligence() {

    try {

        const response =
            await fetch(
                "/api/intelligence?days=30"
            );

        if (!response.ok) {

            throw new Error(
                "Dashboard API failed"
            );

        }

        const data =
            await response.json();

        window.diaMindDashboard =
            data;

        updateDashboardScore(
            data
        );

        updateDashboardMetrics(
            data
        );

        updateDashboardInsights(
            data
        );

    } catch (error) {

        console.error(
            "Dashboard intelligence error:",
            error
        );

    }
}


function updateDashboardScore(
    data
) {

    const score =
        data?.overall?.score;

    const element =
        document.querySelector(
            "[data-dashboard-score]"
        );

    if (
        element &&
        score !== undefined
    ) {

        element.textContent =
            score;

    }

    const status =
        document.querySelector(
            "[data-dashboard-status]"
        );

    if (status) {

        status.textContent =
            data?.overall?.status
            ||
            "Collecting data";

    }
}


function updateDashboardMetrics(
    data
) {

    const glucose =
        data?.glucose;

    const wellness =
        data?.wellness;

    const activity =
        data?.activity;

    setDashboardValue(
        "[data-dashboard-glucose]",
        glucose?.latest,
        " mg/dL"
    );

    setDashboardValue(
        "[data-dashboard-stress]",
        wellness?.stress?.latest
    );

    setDashboardValue(
        "[data-dashboard-sleep]",
        wellness?.sleep?.latest,
        " hrs"
    );

    setDashboardValue(
        "[data-dashboard-steps]",
        activity?.steps?.latest
    );
}


function updateDashboardInsights(
    data
) {

    const element =
        document.querySelector(
            "[data-ai-pattern]"
        );

    if (!element) return;

    const patterns =
        data?.patterns || [];

    if (!patterns.length) {

        element.innerHTML = `
            <strong>Personal pattern discovery</strong>
            <p>
                Keep logging data to allow DiaMind AI
                to discover relationships.
            </p>
        `;

        return;
    }

    const pattern =
        patterns[0];

    element.innerHTML = `

        <strong>
            ${escapeHtml(
                pattern.name
            )}
        </strong>

        <p>
            ${escapeHtml(
                pattern.strength
            )} relationship
        </p>

        <small>
            Correlation:
            ${pattern.correlation ?? "--"}
        </small>

    `;
}


function setDashboardValue(
    selector,
    value,
    suffix = ""
) {

    const element =
        document.querySelector(
            selector
        );

    if (!element) return;

    if (
        value === null ||
        value === undefined
    ) {

        element.textContent =
            "--";

        return;

    }

    element.textContent =
        `${value}${suffix}`;
}


function escapeHtml(
    value
) {

    return String(
        value ?? ""
    )
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}