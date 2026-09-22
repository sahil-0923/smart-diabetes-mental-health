import os
import sys
sys.path.insert(0, os.path.abspath("."))
import json
import pickle
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, root_mean_squared_error

from ai.preprocessor import DiaTrendPreprocessor
from ai.model import build_gru_model

def train_pipeline():
    os.makedirs("ai/artifacts", exist_ok=True)
    os.makedirs("docs", exist_ok=True)
    
    # 1. Preprocessing and sequence creation
    preprocessor = DiaTrendPreprocessor(sequence_length=36, horizon_30=6, horizon_60=12)
    (X_train, y_train), (X_val, y_val), (X_test, y_test), split_info = preprocessor.load_all_subjects()
    
    print(f"Dataset shapes: Train={X_train.shape}, Val={X_val.shape}, Test={X_test.shape}")
    
    # 2. Normalization - Fit scaler ONLY on training data
    # Reshape (N, 36, 5) -> (N*36, 5) to fit scaler
    num_features = X_train.shape[2]
    X_train_flat = X_train.reshape(-1, num_features)
    
    scaler = StandardScaler()
    scaler.fit(X_train_flat)
    
    # Transform inputs
    X_train_scaled = scaler.transform(X_train_flat).reshape(X_train.shape)
    X_val_scaled = scaler.transform(X_val.reshape(-1, num_features)).reshape(X_val.shape)
    X_test_scaled = scaler.transform(X_test.reshape(-1, num_features)).reshape(X_test.shape)
    
    # We also fit a target scaler for glucose or keep targets unscaled for direct regression
    # Predicting raw glucose with Huber loss works directly since values are standard mg/dL (70-250).
    
    # Save Scaler
    scaler_path = "ai/artifacts/scaler.pkl"
    with open(scaler_path, "wb") as f:
        pickle.dump(scaler, f)
    print(f"Scaler saved to {scaler_path}")
    
    # 3. Build & Train Model
    model = build_gru_model(input_shape=(36, 5), output_units=2, learning_rate=0.001)
    
    callbacks = [
        tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=8, restore_best_weights=True, verbose=1),
        tf.keras.callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=3, min_lr=1e-5, verbose=1),
        tf.keras.callbacks.ModelCheckpoint("ai/artifacts/glucose_gru.keras", monitor="val_loss", save_best_only=True, verbose=1)
    ]
    
    print("\nStarting GRU Model Training...")
    history = model.fit(
        X_train_scaled, y_train,
        validation_data=(X_val_scaled, y_val),
        epochs=30,
        batch_size=64,
        callbacks=callbacks,
        verbose=1
    )
    
    # 4. Evaluation on Unseen Test Subjects
    print("\nEvaluating on Test Subjects...")
    y_pred = model.predict(X_test_scaled) # Shape: (N, 2)
    
    # Metrics for 30-min horizon
    y_test_30 = y_test[:, 0]
    y_pred_30 = y_pred[:, 0]
    mae_30 = float(mean_absolute_error(y_test_30, y_pred_30))
    rmse_30 = float(root_mean_squared_error(y_test_30, y_pred_30))
    
    # Metrics for 60-min horizon
    y_test_60 = y_test[:, 1]
    y_pred_60 = y_pred[:, 1]
    mae_60 = float(mean_absolute_error(y_test_60, y_pred_60))
    rmse_60 = float(root_mean_squared_error(y_test_60, y_pred_60))
    
    # 5. Baseline Comparison: Persistence ("Last Known Glucose")
    # Last glucose is at index 35 (the last timestep of the input window) for feature 0 (glucose)
    last_glucose_unscaled = X_test[:, -1, 0]
    
    base_mae_30 = float(mean_absolute_error(y_test_30, last_glucose_unscaled))
    base_rmse_30 = float(root_mean_squared_error(y_test_30, last_glucose_unscaled))
    
    base_mae_60 = float(mean_absolute_error(y_test_60, last_glucose_unscaled))
    base_rmse_60 = float(root_mean_squared_error(y_test_60, last_glucose_unscaled))
    
    print(f"\n================ MODEL EVALUATION SUMMARY ================")
    print(f"30-Minute Forecast: GRU MAE = {mae_30:.2f} mg/dL | Baseline MAE = {base_mae_30:.2f} mg/dL")
    print(f"30-Minute Forecast: GRU RMSE = {rmse_30:.2f} mg/dL | Baseline RMSE = {base_rmse_30:.2f} mg/dL")
    print(f"60-Minute Forecast: GRU MAE = {mae_60:.2f} mg/dL | Baseline MAE = {base_mae_60:.2f} mg/dL")
    print(f"60-Minute Forecast: GRU RMSE = {rmse_60:.2f} mg/dL | Baseline RMSE = {base_rmse_60:.2f} mg/dL")
    print(f"==========================================================\n")
    
    # 6. Save Metadata
    metadata = {
        "model_version": "v1.0.0-gru-diatrend",
        "dataset": "DiaTrend Longitudinal Dataset (54 subjects)",
        "input_features": preprocessor.feature_names,
        "sequence_length": 36,
        "prediction_horizons_min": [30, 60],
        "training_subjects_count": len(split_info["train_subjects"]),
        "validation_subjects_count": len(split_info["val_subjects"]),
        "test_subjects_count": len(split_info["test_subjects"]),
        "metrics": {
            "30_min": {"gru_mae": round(mae_30, 2), "gru_rmse": round(rmse_30, 2), "baseline_mae": round(base_mae_30, 2), "baseline_rmse": round(base_rmse_30, 2)},
            "60_min": {"gru_mae": round(mae_60, 2), "gru_rmse": round(rmse_60, 2), "baseline_mae": round(base_mae_60, 2), "baseline_rmse": round(base_rmse_60, 2)}
        },
        "scaler_means": scaler.mean_.tolist(),
        "scaler_scales": scaler.scale_.tolist()
    }
    
    with open("ai/artifacts/model_metadata.json", "w") as f:
        json.dump(metadata, f, indent=4)
        
    # 7. Generate MODEL_REPORT.md
    report_content = f"""# DiabetesAI GRU Forecasting Model Report

## 1. Dataset Overview
- **Source:** DiaTrend Longitudinal Dataset
- **Total Subjects:** {len(split_info["train_subjects"]) + len(split_info["val_subjects"]) + len(split_info["test_subjects"])}
- **Training Subjects ({len(split_info["train_subjects"])}):** {', '.join(split_info["train_subjects"][:10])}...
- **Validation Subjects ({len(split_info["val_subjects"])}):** {', '.join(split_info["val_subjects"])}
- **Test Subjects ({len(split_info["test_subjects"])}):** {', '.join(split_info["test_subjects"])}
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
| **30-Minute** | **{mae_30:.2f}** | **{rmse_30:.2f}** | {base_mae_30:.2f} | {base_rmse_30:.2f} |
| **60-Minute** | **{mae_60:.2f}** | **{rmse_60:.2f}** | {base_mae_60:.2f} | {base_rmse_60:.2f} |

## 4. Limitations & Medical Safety
- This model serves as an informational AI forecast prototype for educational and decision-support purposes.
- It does not replace clinical glucose monitoring or medical diagnosis.
"""
    with open("docs/MODEL_REPORT.md", "w") as f:
        f.write(report_content)
        
    print("Training pipeline completed and artifacts generated successfully!")

if __name__ == "__main__":
    train_pipeline()
