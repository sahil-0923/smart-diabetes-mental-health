import os
import sys
sys.path.insert(0, os.path.abspath("."))
import pickle
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.metrics import mean_absolute_error, root_mean_squared_error

def run_real_cgm_validation():
    print("=" * 80)
    print("REAL CGM VALIDATION EXPERIMENT ON UNSEEN TEST SUBJECTS (DiaTrend)")
    print("=" * 80)

    # 1. Load existing trained model and scaler
    model_path = "ai/artifacts/glucose_gru.keras"
    scaler_path = "ai/artifacts/scaler.pkl"
    
    if not os.path.exists(model_path) or not os.path.exists(scaler_path):
        print(f"Error: Model or Scaler not found in ai/artifacts/")
        return

    model = tf.keras.models.load_model(model_path)
    with open(scaler_path, "rb") as f:
        scaler = pickle.load(f)

    # 2. Select test subjects (subject_46 to subject_54) - Unseen in training
    test_subjects = [f"subject_{i:02d}" for i in range(46, 55)]
    base_dir = "data/longitudinal/DiaTrend"

    all_windows_X = []
    all_y_true_30 = []
    all_y_true_60 = []
    all_baseline_30 = []
    all_baseline_60 = []
    
    sample_window_detail = None
    total_valid_windows = 0

    for subj in test_subjects:
        subj_dir = os.path.join(base_dir, subj)
        cgm_path = os.path.join(subj_dir, "cgm.csv")
        steps_path = os.path.join(subj_dir, "steps.csv")
        sleep_path = os.path.join(subj_dir, "sleep.csv")

        if not os.path.exists(cgm_path):
            continue

        df_cgm = pd.read_csv(cgm_path)
        df_cgm['timestamp'] = pd.to_datetime(df_cgm['timestamp'])
        df_cgm = df_cgm.sort_values('timestamp').reset_index(drop=True)

        df_steps = pd.read_csv(steps_path) if os.path.exists(steps_path) else pd.DataFrame(columns=['timestamp', 'steps'])
        df_steps['timestamp'] = pd.to_datetime(df_steps['timestamp'])
        step_dict = dict(zip(df_steps['timestamp'], df_steps['steps']))

        df_sleep = pd.read_csv(sleep_path) if os.path.exists(sleep_path) else pd.DataFrame(columns=['start_time', 'end_time'])
        sleep_intervals = []
        if not df_sleep.empty:
            df_sleep['start_time'] = pd.to_datetime(df_sleep['start_time'])
            df_sleep['end_time'] = pd.to_datetime(df_sleep['end_time'])
            sleep_intervals = list(zip(df_sleep['start_time'], df_sleep['end_time']))

        # Extract features into precomputed columns for speed
        n_rows = len(df_cgm)
        timestamps = df_cgm['timestamp'].tolist()
        glucoses = df_cgm['glucose'].tolist()

        step_col = [float(step_dict.get(ts, 0.0)) for ts in timestamps]
        
        sleep_col = []
        for ts in timestamps:
            is_sl = 0.0
            for s_start, s_end in sleep_intervals:
                if s_start <= ts <= s_end:
                    is_sl = 1.0
                    break
            sleep_col.append(is_sl)

        hours = np.array([ts.hour + ts.minute / 60.0 for ts in timestamps])
        hour_sin = np.sin(2 * np.pi * hours / 24.0)
        hour_cos = np.cos(2 * np.pi * hours / 24.0)

        # Feature matrix for this subject
        full_feat_matrix = np.column_stack([
            np.array(glucoses, dtype=np.float32),
            np.array(step_col, dtype=np.float32),
            np.array(sleep_col, dtype=np.float32),
            np.array(hour_sin, dtype=np.float32),
            np.array(hour_cos, dtype=np.float32)
        ])

        # Find continuous sequences of at least 48 valid 5-minute readings (36 input + 12 future horizon)
        for start_idx in range(0, n_rows - 48, 4):
            # Check timestamps continuity between start_idx and start_idx + 48
            t_start = timestamps[start_idx]
            t_end = timestamps[start_idx + 47]
            # 47 intervals of 5 minutes = 235 minutes
            total_span_min = (t_end - t_start).total_seconds() / 60.0
            
            # If span is within +/- 15 min of 235 min, it is continuous
            if abs(total_span_min - 235.0) > 15.0:
                continue

            input_36_feat = full_feat_matrix[start_idx : start_idx + 36]
            y_30 = glucoses[start_idx + 36 + 6 - 1] # 6 readings ahead (+30 min)
            y_60 = glucoses[start_idx + 36 + 12 - 1] # 12 readings ahead (+60 min)
            last_known_glucose = glucoses[start_idx + 35]

            all_windows_X.append(input_36_feat)
            all_y_true_30.append(y_30)
            all_y_true_60.append(y_60)
            all_baseline_30.append(last_known_glucose)
            all_baseline_60.append(last_known_glucose)
            total_valid_windows += 1

            if sample_window_detail is None and subj == "subject_46":
                sample_window_detail = {
                    "subject": subj,
                    "timestamps": timestamps[start_idx : start_idx + 36],
                    "glucoses": glucoses[start_idx : start_idx + 36],
                    "feature_matrix": input_36_feat,
                    "target_30_time": timestamps[start_idx + 36 + 6 - 1],
                    "target_30_val": y_30,
                    "target_60_time": timestamps[start_idx + 36 + 12 - 1],
                    "target_60_val": y_60,
                    "last_known_glucose": last_known_glucose
                }

    print(f"Total Test Subjects Tested: {len(test_subjects)} ({', '.join(test_subjects)})")
    print(f"Total Continuous 48-Point Real Windows Evaluated: {total_valid_windows}")
    print(f"Input Matrix Shape per Window: (36, 5) -> 36 consecutive 5-min real readings")

    # 3. Batch Predict with Trained GRU
    X_all = np.array(all_windows_X, dtype=np.float32) # Shape: (N, 36, 5)
    
    # Scale inputs using existing scaler.pkl
    X_flat = X_all.reshape(-1, 5)
    X_scaled = scaler.transform(X_flat).reshape(X_all.shape)

    # Predict
    preds = model.predict(X_scaled, batch_size=256, verbose=0) # Shape: (N, 2)
    preds_30 = preds[:, 0]
    preds_60 = preds[:, 1]

    y_true_30 = np.array(all_y_true_30)
    y_true_60 = np.array(all_y_true_60)
    base_30 = np.array(all_baseline_30)
    base_60 = np.array(all_baseline_60)

    # 4. Metrics Calculation
    gru_mae_30 = float(mean_absolute_error(y_true_30, preds_30))
    gru_rmse_30 = float(root_mean_squared_error(y_true_30, preds_30))
    base_mae_30 = float(mean_absolute_error(y_true_30, base_30))
    base_rmse_30 = float(root_mean_squared_error(y_true_30, base_30))

    gru_mae_60 = float(mean_absolute_error(y_true_60, preds_60))
    gru_rmse_60 = float(root_mean_squared_error(y_true_60, preds_60))
    base_mae_60 = float(mean_absolute_error(y_true_60, base_60))
    base_rmse_60 = float(root_mean_squared_error(y_true_60, base_60))

    imp_mae_30 = ((base_mae_30 - gru_mae_30) / base_mae_30) * 100.0
    imp_rmse_30 = ((base_rmse_30 - gru_rmse_30) / base_rmse_30) * 100.0
    imp_mae_60 = ((base_mae_60 - gru_mae_60) / base_mae_60) * 100.0
    imp_rmse_60 = ((base_rmse_60 - gru_rmse_60) / base_rmse_60) * 100.0

    print("\n" + "=" * 80)
    print("## REAL CGM GRU VALIDATION")
    print("=" * 80)
    print(f"Subjects tested: {len(test_subjects)} ({test_subjects[0]} to {test_subjects[-1]})")
    print(f"Number of windows: {total_valid_windows}")
    print(f"Input: 36 REAL CGM readings")
    print(f"Sampling: approximately 5 minutes")
    print(f"Prediction horizons: 30 min / 60 min")
    print("-" * 80)
    print("30-MIN:")
    print(f"GRU MAE:         {gru_mae_30:.2f} mg/dL")
    print(f"GRU RMSE:        {gru_rmse_30:.2f} mg/dL")
    print(f"Baseline MAE:    {base_mae_30:.2f} mg/dL")
    print(f"Baseline RMSE:   {base_rmse_30:.2f} mg/dL")
    print("-" * 80)
    print("60-MIN:")
    print(f"GRU MAE:         {gru_mae_60:.2f} mg/dL")
    print(f"GRU RMSE:        {gru_rmse_60:.2f} mg/dL")
    print(f"Baseline MAE:    {base_mae_60:.2f} mg/dL")
    print(f"Baseline RMSE:   {base_rmse_60:.2f} mg/dL")
    print("-" * 80)
    print("GRU improvement over baseline:")
    print(f"  • 30-min MAE reduction:  {imp_mae_30:.1f}% ({gru_mae_30:.2f} vs {base_mae_30:.2f} mg/dL)")
    print(f"  • 30-min RMSE reduction: {imp_rmse_30:.1f}% ({gru_rmse_30:.2f} vs {base_rmse_30:.2f} mg/dL)")
    print(f"  • 60-min MAE reduction:  {imp_mae_60:.1f}% ({gru_mae_60:.2f} vs {base_mae_60:.2f} mg/dL)")
    print(f"  • 60-min RMSE reduction: {imp_rmse_60:.1f}% ({gru_rmse_60:.2f} vs {base_rmse_60:.2f} mg/dL)")
    print("=" * 80)

    # 5. Detail for ONE Sample Window
    print("\n" + "=" * 80)
    print(f"SAMPLE REAL CGM WINDOW INSPECTION ({sample_window_detail['subject']})")
    print("=" * 80)
    for idx in range(36):
        ts = sample_window_detail['timestamps'][idx]
        g = sample_window_detail['glucoses'][idx]
        print(f"{idx+1:2d}. actual: timestamp={ts.strftime('%Y-%m-%d %H:%M:%S')} | glucose={g:.1f} mg/dL")

    # Predict on this single window
    sample_feat = sample_window_detail['feature_matrix'].reshape(1, 36, 5)
    sample_scaled = scaler.transform(sample_feat.reshape(-1, 5)).reshape(1, 36, 5)
    sample_pred = model.predict(sample_scaled, verbose=0)
    sample_pred_30 = float(sample_pred[0, 0])
    sample_pred_60 = float(sample_pred[0, 1])

    sample_true_30 = float(sample_window_detail['target_30_val'])
    sample_true_60 = float(sample_window_detail['target_60_val'])
    sample_last = sample_window_detail['last_known_glucose']

    err_30_gru = abs(sample_pred_30 - sample_true_30)
    err_60_gru = abs(sample_pred_60 - sample_true_60)

    print("\n" + "-" * 80)
    print(f"Latest actual input:      {sample_last:.1f} mg/dL ({sample_window_detail['timestamps'][-1].strftime('%Y-%m-%d %H:%M:%S')})")
    print(f"GRU 30-min prediction:    {sample_pred_30:.1f} mg/dL")
    print(f"Actual 30-min glucose:    {sample_true_30:.1f} mg/dL ({sample_window_detail['target_30_time'].strftime('%Y-%m-%d %H:%M:%S')})")
    print(f"30-min error:             {err_30_gru:.2f} mg/dL")
    print("-" * 80)
    print(f"GRU 60-min prediction:    {sample_pred_60:.1f} mg/dL")
    print(f"Actual 60-min glucose:    {sample_true_60:.1f} mg/dL ({sample_window_detail['target_60_time'].strftime('%Y-%m-%d %H:%M:%S')})")
    print(f"60-min error:             {err_60_gru:.2f} mg/dL")
    print("=" * 80)

if __name__ == "__main__":
    run_real_cgm_validation()
