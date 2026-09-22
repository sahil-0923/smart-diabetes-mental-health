# DiabetesAI Internal APIs (Phase 1C)

This document describes the historical health data APIs designed to feed the frontend charts and metrics. 

**Authentication:** 
All endpoints are protected by a session-based `@login_required` decorator. An authenticated session cookie must be present. The API will infer the user from the session and ONLY return the logged-in user's data.

---

## 1. Glucose History
`GET /api/glucose/history`

Returns a chronological array of glucose readings suitable for Chart.js injection.

**Query Parameters:**
- `days` (optional): Integer (1-365). Default: `7`.

**Response (200 OK):**
```json
{
  "success": true,
  "days": 7,
  "labels": ["2026-08-24 11:21", "2026-08-24 18:00"],
  "values": [145.0, 110.0],
  "records": [
    { "id": 12, "timestamp": "2026-08-24 11:21", "glucose": 145.0 }
  ],
  "statistics": {
    "current": 110.0,
    "average": 127.5,
    "highest": 145.0,
    "lowest": 110.0
  }
}
```

---

## 2. Glucose Trend
`GET /api/glucose/trend`

Returns a simple rolling calculation to determine the recent glucose trajectory.

**Query Parameters:**
- `days` (optional): Integer. Default: `7`.

**Response (200 OK):**
```json
{
  "success": true,
  "trend": "stable",
  "change": 0.0,
  "records_used": 3
}
```

---

## 3. Wellness History
`GET /api/wellness/history`

Returns separate arrays for wellness metrics mapped to the same chronological labels.

**Query Parameters:**
- `days` (optional): Integer. Default: `7`.

**Response (200 OK):**
```json
{
  "success": true,
  "labels": ["2026-08-24 11:21"],
  "stress": [7.0],
  "sleep": [6.5],
  "mood": ["7"],
  "steps": [5000],
  "exercise_duration": [30.0]
}
```

---

## 4. Health Trends
`GET /api/health-trends`

A combined endpoint providing all physiological and lifestyle indicators chronologically, ideal for plotting multi-axis correlation charts.

**Query Parameters:**
- `days` (optional): Integer. Default: `7`.

**Response (200 OK):**
```json
{
  "success": true,
  "labels": ["2026-08-24 11:21"],
  "glucose": [145.0],
  "stress": [7.0],
  "sleep": [6.5],
  "steps": [5000],
  "weight": [62.0],
  "mood": ["7"],
  "exercise_duration": [30.0]
}
```

---

## 5. Recent Health Records
`GET /api/health-records/recent`

Returns the raw database records ordered newest-first.

**Query Parameters:**
- `limit` (optional): Integer (1-100). Default: `10`.

**Response (200 OK):**
```json
{
  "success": true,
  "records": [
    {
      "id": 14,
      "timestamp": "2026-08-24 11:21:41",
      "glucose": 180.0,
      "stress": 8.0,
      "sleep": 5.0,
      "steps": 2000,
      "weight": 62.2,
      "mood": "4",
      "meal_context": "Random",
      "exercise_duration": 0.0
    }
  ]
}
```

---

## 6. Health Summary
`GET /api/health/summary`

Provides quick top-level widgets values for dashboard views.

**Response (200 OK):**
```json
{
  "success": true,
  "current_glucose": 180.0,
  "today_average_glucose": 145.0,
  "weekly_average_glucose": 145.0,
  "highest_recent_glucose": 180.0,
  "lowest_recent_glucose": 110.0,
  "latest_stress": 8.0,
  "latest_sleep": 5.0,
  "latest_steps": 2000,
  "latest_weight": 62.2,
  "latest_mood": "4"
}
```

---
**Note:** If a user has no records, the APIs will return a success state with empty arrays (`[]`) and a `message` explaining the absence of records.
