import os
import sys
import glob
import json
import pickle
from datetime import datetime
import pandas as pd
import numpy as np
import tensorflow as tf

sys.path.insert(0, os.path.abspath("."))

from ai.preprocessor import DiaTrendPreprocessor

def full_audit():
    results = {}
    
    # -------------------------------------------------------------
    # 1. DATASET AUDIT
    # -------------------------------------------------------------
    base_dir = "data/longitudinal/DiaTrend"
    subjects = sorted([d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))])
    results["total_subjects"] = len(subjects)
    results["subject_list"] = subjects
    
    cgm_files = []
    steps_files = []
    sleep_files = []
    hr_files = []
    demo_files = []
    
    cgm_row_counts = []
    steps_row_counts = []
    sleep_row_counts = []
    hr_row_counts = []
    
    all_glucose_values = []
    cgm_cols = None
    cgm_time_sample = None
    
    empty_files_count = 0
    missing_values_per_col = {}
    
    for s in subjects:
        s_dir = os.path.join(base_dir, s)
        cgm_p = os.path.join(s_dir, "cgm.csv")
        steps_p = os.path.join(s_dir, "steps.csv")
        sleep_p = os.path.join(s_dir, "sleep.csv")
        hr_p = os.path.join(s_dir, "heart_rate.csv")
        demo_p = os.path.join(s_dir, "demographics.csv")
        
        if os.path.exists(cgm_p):
            cgm_files.append(cgm_p)
            df = pd.read_csv(cgm_p)
            cgm_row_counts.append(len(df))
            if len(df) == 0: empty_files_count += 1
            if cgm_cols is None:
                cgm_cols = list(df.columns)
                cgm_time_sample = str(df["timestamp"].iloc[0]) if "timestamp" in df.columns and len(df) > 0 else "N/A"
            for col in df.columns:
                missing_values_per_col[f"cgm_{col}"] = missing_values_per_col.get(f"cgm_{col}", 0) + int(df[col].isna().sum())
            if "glucose" in df.columns:
                all_glucose_values.extend(df["glucose"].dropna().tolist())
                
        if os.path.exists(steps_p):
            steps_files.append(steps_p)
            df_s = pd.read_csv(steps_p)
            steps_row_counts.append(len(df_s))
            if len(df_s) == 0: empty_files_count += 1
            for col in df_s.columns:
                missing_values_per_col[f"steps_{col}"] = missing_values_per_col.get(f"steps_{col}", 0) + int(df_s[col].isna().sum())
            
        if os.path.exists(sleep_p):
            sleep_files.append(sleep_p)
            df_sl = pd.read_csv(sleep_p)
            sleep_row_counts.append(len(df_sl))
            if len(df_sl) == 0: empty_files_count += 1
            for col in df_sl.columns:
                missing_values_per_col[f"sleep_{col}"] = missing_values_per_col.get(f"sleep_{col}", 0) + int(df_sl[col].isna().sum())
            
        if os.path.exists(hr_p):
            hr_files.append(hr_p)
            df_hr = pd.read_csv(hr_p)
            hr_row_counts.append(len(df_hr))
            if len(df_hr) == 0: empty_files_count += 1
            for col in df_hr.columns:
                missing_values_per_col[f"hr_{col}"] = missing_values_per_col.get(f"hr_{col}", 0) + int(df_hr[col].isna().sum())
            
        if os.path.exists(demo_p):
            demo_files.append(demo_p)

    results["cgm_files_count"] = len(cgm_files)
    results["steps_files_count"] = len(steps_files)
    results["sleep_files_count"] = len(sleep_files)
    results["hr_files_count"] = len(hr_files)
    results["demo_files_count"] = len(demo_files)
    results["empty_files_count"] = empty_files_count
    results["missing_values_per_col"] = missing_values_per_col
    
    results["total_cgm_rows"] = sum(cgm_row_counts)
    results["total_steps_rows"] = sum(steps_row_counts)
    results["total_sleep_rows"] = sum(sleep_row_counts)
    results["total_hr_rows"] = sum(hr_row_counts)
    
    results["min_cgm_per_subject"] = int(np.min(cgm_row_counts))
    results["max_cgm_per_subject"] = int(np.max(cgm_row_counts))
    results["avg_cgm_per_subject"] = float(np.mean(cgm_row_counts))
    
    g_arr = np.array(all_glucose_values)
    results["cgm_columns"] = cgm_cols
    results["cgm_time_sample"] = cgm_time_sample
    results["glucose_count"] = len(g_arr)
    results["glucose_min"] = float(np.min(g_arr))
    results["glucose_max"] = float(np.max(g_arr))
    results["glucose_mean"] = float(np.mean(g_arr))
    results["glucose_median"] = float(np.median(g_arr))

    # -------------------------------------------------------------
    # 2. SUBJECT SPLIT & PREPROCESSING SEQUENCE GENERATION
    # -------------------------------------------------------------
    preprocessor = DiaTrendPreprocessor(sequence_length=36, horizon_30=6, horizon_60=12)
    (X_train, y_train), (X_val, y_val), (X_test, y_test), split_info = preprocessor.load_all_subjects(base_dir=base_dir)
    
    results["split_info"] = split_info
    results["X_train_shape"] = list(X_train.shape)
    results["y_train_shape"] = list(y_train.shape)
    results["X_val_shape"] = list(X_val.shape)
    results["y_val_shape"] = list(y_val.shape)
    results["X_test_shape"] = list(X_test.shape)
    results["y_test_shape"] = list(y_test.shape)
    
    # Calculate preprocessed aligned rows per split
    def count_aligned_rows(subs):
        total_rows = 0
        for s in subs:
            df = preprocessor.load_subject_data(os.path.join(base_dir, s))
            if df is not None:
                total_rows += len(df)
        return total_rows
        
    results["aligned_rows_train"] = count_aligned_rows(split_info["train_subjects"])
    results["aligned_rows_val"] = count_aligned_rows(split_info["val_subjects"])
    results["aligned_rows_test"] = count_aligned_rows(split_info["test_subjects"])
    results["aligned_rows_total"] = results["aligned_rows_train"] + results["aligned_rows_val"] + results["aligned_rows_test"]

    # -------------------------------------------------------------
    # 3. ARTIFACTS AUDIT & EVALUATION
    # -------------------------------------------------------------
    model_path = "ai/artifacts/glucose_gru.keras"
    scaler_path = "ai/artifacts/scaler.pkl"
    meta_path = "ai/artifacts/model_metadata.json"
    
    results["model_file_exists"] = os.path.exists(model_path)
    results["model_file_size"] = os.path.getsize(model_path) if results["model_file_exists"] else 0
    results["model_file_mtime"] = datetime.fromtimestamp(os.path.getmtime(model_path)).isoformat() if results["model_file_exists"] else ""
    
    results["scaler_file_exists"] = os.path.exists(scaler_path)
    results["scaler_file_size"] = os.path.getsize(scaler_path) if results["scaler_file_exists"] else 0
    results["scaler_file_mtime"] = datetime.fromtimestamp(os.path.getmtime(scaler_path)).isoformat() if results["scaler_file_exists"] else ""
    
    results["meta_file_exists"] = os.path.exists(meta_path)
    results["meta_file_size"] = os.path.getsize(meta_path) if results["meta_file_exists"] else 0
    results["meta_file_mtime"] = datetime.fromtimestamp(os.path.getmtime(meta_path)).isoformat() if results["meta_file_exists"] else ""
    
    if results["meta_file_exists"]:
        with open(meta_path, "r") as f:
            results["metadata_content"] = json.load(f)
            
    # Load Scaler
    with open(scaler_path, "rb") as f:
        scaler = pickle.load(f)
    results["scaler_mean"] = list(scaler.mean_)
    results["scaler_scale"] = list(scaler.scale_)
    
    # Load Model
    model = tf.keras.models.load_model(model_path)
    results["loaded_input_shape"] = list(model.input_shape)
    results["loaded_output_shape"] = list(model.output_shape)
    results["total_params"] = int(model.count_params())
    
    # Check weight statistics
    layer_weight_stats = []
    for l in model.layers:
        weights = l.get_weights()
        if weights:
            w_arr = weights[0]
            layer_weight_stats.append({
                "layer_name": l.name,
                "weight_shape": list(w_arr.shape),
                "weight_mean": float(np.mean(w_arr)),
                "weight_std": float(np.std(w_arr)),
                "weight_min": float(np.min(w_arr)),
                "weight_max": float(np.max(w_arr))
            })
    results["layer_weight_stats"] = layer_weight_stats
    
    # Evaluate on Test Set using the saved scaler
    num_features = X_test.shape[2]
    X_test_scaled = scaler.transform(X_test.reshape(-1, num_features)).reshape(X_test.shape)
    
    preds = model.predict(X_test_scaled, batch_size=64, verbose=0)
    
    gru_mae_30 = float(np.mean(np.abs(preds[:, 0] - y_test[:, 0])))
    gru_rmse_30 = float(np.sqrt(np.mean(np.square(preds[:, 0] - y_test[:, 0]))))
    gru_mae_60 = float(np.mean(np.abs(preds[:, 1] - y_test[:, 1])))
    gru_rmse_60 = float(np.sqrt(np.mean(np.square(preds[:, 1] - y_test[:, 1]))))
    
    # Persistence baseline
    last_glucose_unscaled = X_test[:, -1, 0]
    
    base_mae_30 = float(np.mean(np.abs(last_glucose_unscaled - y_test[:, 0])))
    base_rmse_30 = float(np.sqrt(np.mean(np.square(last_glucose_unscaled - y_test[:, 0]))))
    base_mae_60 = float(np.mean(np.abs(last_glucose_unscaled - y_test[:, 1])))
    base_rmse_60 = float(np.sqrt(np.mean(np.square(last_glucose_unscaled - y_test[:, 1]))))
    
    results["eval_gru_mae_30"] = gru_mae_30
    results["eval_gru_rmse_30"] = gru_rmse_30
    results["eval_gru_mae_60"] = gru_mae_60
    results["eval_gru_rmse_60"] = gru_rmse_60
    
    results["eval_base_mae_30"] = base_mae_30
    results["eval_base_rmse_30"] = base_rmse_30
    results["eval_base_mae_60"] = base_mae_60
    results["eval_base_rmse_60"] = base_rmse_60

    print("AUDIT_RESULTS_JSON_START")
    print(json.dumps(results, indent=2))
    print("AUDIT_RESULTS_JSON_END")

if __name__ == "__main__":
    full_audit()
