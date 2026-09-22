# DiabetesAI GRU Forecasting Model Report

## 1. Dataset Overview
- **Source:** DiaTrend Longitudinal Dataset
- **Total Subjects:** 54
- **Training Subjects (37):** subject_01, subject_02, subject_03, subject_04, subject_05, subject_06, subject_07, subject_08, subject_09, subject_10...
- **Validation Subjects (8):** subject_38, subject_39, subject_40, subject_41, subject_42, subject_43, subject_44, subject_45
- **Test Subjects (9):** subject_46, subject_47, subject_48, subject_49, subject_50, subject_51, subject_52, subject_53, subject_54
- **Temporal Resolution:** 5-minute continuous grid

## 2. Input Features & Architecture
- **Features:** `['glucose', 'steps', 'is_sleeping', 'hour_sin', 'hour_cos']`
- **Input Sequence Length:** 36 timesteps (180 minutes / 3 hours)
- **Architecture:**
  - `GRU(64, return_sequences=True)` + `Dropout(0.2)`
  - `GRU(32, return_sequences=False)` + `Dropout(0.2)`
  - `Dense(32, activation='relu')`
  - `Dense(2, activation='linear')` -> `[y_30, y_60]`
- **Loss Function:** Huber Loss ($\delta=1.0$)
- **Optimizer:** Adam ($lr=0.001$ with ReduceLROnPlateau)

## 3. Evaluation & Baseline Comparison (On Unseen Test Subjects)
| Horizon | GRU MAE (mg/dL) | GRU RMSE (mg/dL) | Persistence Baseline MAE | Persistence Baseline RMSE |
|---|---|---|---|---|
| **30-Minute** | **4.36** | **5.49** | 5.46 | 6.90 |
| **60-Minute** | **5.10** | **6.42** | 7.68 | 9.74 |

## 4. Limitations & Medical Safety
- This model serves as an informational AI forecast prototype for educational and decision-support purposes.
- It does not replace clinical glucose monitoring or medical diagnosis.
