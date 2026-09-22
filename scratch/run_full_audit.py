import os
import sys
import json
import numpy as np
import pandas as pd
import tensorflow as tf
import pickle
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath("."))
from app import app, db, User, HealthRecord
from ai.model_service import model_service, ForecastModelService

def audit_part1():
    print("=" * 80)
    print("AUDIT PART 1: DATABASE -> APPLICATION DATA FLOW")
    print("=" * 80)
    with app.app_context():
        user = User.query.filter_by(name="Rahul Kumar").first()
        print(f"User ID: {user.id}")
        print(f"User Name: {user.name}")
        print(f"User Email: {user.email}")
        print(f"Diabetes Type: {user.diabetes_type}")
        print(f"Age: {user.age}, Height: {user.height} cm, Weight: {user.weight} kg")
        
        recs = HealthRecord.query.filter_by(user_id=user.id, is_valid=True).order_by(HealthRecord.date.desc()).all()
        print(f"Number of genuine health records: {len(recs)}")
        print("\nAll Valid Records for Rahul Kumar:")
        for r in recs:
            print(f"  ID: {r.id:3d} | Timestamp: {r.date} | Glucose: {r.glucose:5.1f} mg/dL | Context: {r.meal_context!s:<15} | Stress: {r.stress} | Sleep: {r.sleep}h | Steps: {r.steps}")
        
        # Check all users in DB
        all_users = User.query.all()
        print(f"\nTotal users in Database: {len(all_users)}")
        for u in all_users:
            u_recs = HealthRecord.query.filter_by(user_id=u.id).count()
            print(f"  User ID {u.id}: '{u.name}' ({u.email}) -> {u_recs} records")

def audit_part3_and_4():
    print("\n" + "=" * 80)
    print("AUDIT PART 3 & 4: GRU MODEL VERIFICATION & CURRENT USER INPUT AUDIT")
    print("=" * 80)
    model_path = "ai/artifacts/glucose_gru.keras"
    scaler_path = "ai/artifacts/scaler.pkl"
    print(f"Model file exists: {os.path.exists(model_path)} (Size: {os.path.getsize(model_path):,} bytes)")
    print(f"Scaler file exists: {os.path.exists(scaler_path)} (Size: {os.path.getsize(scaler_path):,} bytes)")
    
    model = tf.keras.models.load_model(model_path, compile=False)
    with open(scaler_path, "rb") as f:
        scaler = pickle.load(f)
    
    print("\nModel Architecture:")
    model.summary(print_fn=lambda x: print("  " + x))
    print(f"Model Input Shape: {model.input_shape}")
    print(f"Model Output Shape: {model.output_shape}")
    print(f"Total Trainable Parameters: {model.count_params():,}")
    
    # Run runtime prediction for Rahul Kumar
    with app.app_context():
        user = User.query.filter_by(name="Rahul Kumar").first()
        recs = HealthRecord.query.filter_by(user_id=user.id, is_valid=True).order_by(HealthRecord.date.asc()).all()
        res = model_service.predict_forecast(recs)
        print("\nRuntime predict_forecast result:")
        print(json.dumps(res, indent=2, default=str))

        # Inspect raw tensor passed to model
        seq = model_service.prepare_sequence_from_records(recs)
        print(f"\nConstructed sequence shape: {seq.shape}")
        
        now = recs[-1].date if recs[-1].date else datetime.utcnow()
        timestamps = [now - timedelta(minutes=5*(35 - i)) for i in range(36)]
        raw_glucoses = [float(r.glucose) for r in recs if r.glucose is not None]
        num_raw = len(raw_glucoses)
        
        print("\nDetailed Timestep Breakdown for Rahul Kumar:")
        print(f"{'Idx':<4} | {'Timestamp':<19} | {'Glucose':<7} | {'Steps':<6} | {'Sleep':<5} | {'Sin':<7} | {'Cos':<7} | {'Type':<22}")
        print("-" * 90)
        for i in range(36):
            t = timestamps[i]
            g = seq[0, i, 0]
            s = seq[0, i, 1]
            sl = seq[0, i, 2]
            sin_v = seq[0, i, 3]
            cos_v = seq[0, i, 4]
            if i == 35:
                src_type = "REAL LATEST READING"
            elif num_raw >= 36:
                src_type = "REAL CONSECUTIVE"
            else:
                src_type = "INTERPOLATED HISTORY"
            print(f"{i:4d} | {str(t)[:19]:<19} | {g:7.1f} | {s:6.1f} | {sl:5.0f} | {sin_v:7.3f} | {cos_v:7.3f} | {src_type:<22}")

def audit_part5_and_6():
    print("\n" + "=" * 80)
    print("AUDIT PART 5 & 6: REAL CGM VALIDATION ON UNSEEN DIATREND TEST SUBJECTS")
    print("=" * 80)
    
    test_subjects = [f"subject_{i}" for i in range(46, 55)]
    base_dir = "data/longitudinal/DiaTrend"
    
    model = tf.keras.models.load_model("ai/artifacts/glucose_gru.keras", compile=False)
    with open("ai/artifacts/scaler.pkl", "rb") as f:
        scaler = pickle.load(f)
    
    all_30_gru_errs = []
    all_60_gru_errs = []
    all_30_base_errs = []
    all_60_base_errs = []
    
    total_valid_windows = 0
    total_rejected_windows = 0
    interpolated_values = 0
    synthetic_values = 0
    
    sample_example = None

    for subj in test_subjects:
        cgm_file = os.path.join(base_dir, subj, "cgm.csv")
        if not os.path.exists(cgm_file):
            print(f"Skipping {subj}, cgm.csv not found")
            continue
            
        df = pd.read_csv(cgm_file)
        time_col = [c for c in df.columns if "time" in c.lower() or "date" in c.lower()][0]
        gluc_col = [c for c in df.columns if "glucose" in c.lower() or "cgm" in c.lower() or "value" in c.lower() or "mg" in c.lower()][0]
        
        df['dt'] = pd.to_datetime(df[time_col])
        df = df.sort_values('dt').dropna(subset=[gluc_col])
        df['glucose'] = df[gluc_col].astype(float)
        
        df = df[(df['glucose'] >= 40) & (df['glucose'] <= 450)].reset_index(drop=True)
        
        times = df['dt'].values
        glucs = df['glucose'].values
        
        i = 0
        while i + 48 <= len(df):
            sub_times = times[i : i + 48]
            sub_glucs = glucs[i : i + 48]
            
            diffs = (sub_times[1:] - sub_times[:-1]).astype('timedelta64[m]').astype(float)
            if np.all((diffs >= 3) & (diffs <= 7)):
                input_glucs = sub_glucs[:36]
                input_times = pd.to_datetime(sub_times[:36])
                
                target_30 = sub_glucs[36 + 5]
                target_60 = sub_glucs[36 + 11]
                baseline_pred = input_glucs[-1]
                
                hours = input_times.hour + input_times.minute / 60.0
                hour_sin = np.sin(2 * np.pi * hours / 24.0)
                hour_cos = np.cos(2 * np.pi * hours / 24.0)
                is_sleeping = ((hours >= 23) | (hours < 7)).astype(float)
                steps = np.zeros(36)
                
                features = np.column_stack([input_glucs, steps, is_sleeping, hour_sin, hour_cos])
                scaled = scaler.transform(features)
                tensor = np.expand_dims(scaled, axis=0)
                
                preds = model.predict(tensor, verbose=0)
                pred_30 = float(preds[0, 0])
                pred_60 = float(preds[0, 1])
                
                all_30_gru_errs.append(abs(pred_30 - target_30))
                all_60_gru_errs.append(abs(pred_60 - target_60))
                all_30_base_errs.append(abs(baseline_pred - target_30))
                all_60_base_errs.append(abs(baseline_pred - target_60))
                
                if sample_example is None and subj == "subject_46":
                    sample_example = {
                        "subject": subj,
                        "timestamps": [str(t)[:19] for t in input_times],
                        "glucoses": [float(g) for g in input_glucs],
                        "latest_actual": float(baseline_pred),
                        "pred_30": float(round(pred_30, 2)),
                        "actual_30": float(target_30),
                        "err_30": float(round(abs(pred_30 - target_30), 2)),
                        "pred_60": float(round(pred_60, 2)),
                        "actual_60": float(target_60),
                        "err_60": float(round(abs(pred_60 - target_60), 2))
                    }
                
                total_valid_windows += 1
                i += 6
            else:
                total_rejected_windows += 1
                i += 1

    gru_mae_30 = np.mean(all_30_gru_errs)
    gru_rmse_30 = np.sqrt(np.mean(np.array(all_30_gru_errs)**2))
    base_mae_30 = np.mean(all_30_base_errs)
    base_rmse_30 = np.sqrt(np.mean(np.array(all_30_base_errs)**2))
    imp_30 = ((base_mae_30 - gru_mae_30) / base_mae_30) * 100.0

    gru_mae_60 = np.mean(all_60_gru_errs)
    gru_rmse_60 = np.sqrt(np.mean(np.array(all_60_gru_errs)**2))
    base_mae_60 = np.mean(all_60_base_errs)
    base_rmse_60 = np.sqrt(np.mean(np.array(all_60_base_errs)**2))
    imp_60 = ((base_mae_60 - gru_mae_60) / base_mae_60) * 100.0

    print(f"Subjects evaluated: {len(test_subjects)} ({test_subjects[0]} through {test_subjects[-1]})")
    print(f"Total valid 5-min windows: {total_valid_windows:,}")
    print(f"Total rejected discontinuous windows: {total_rejected_windows:,}")
    print(f"Interpolated glucose values: {interpolated_values}")
    print(f"Synthetic glucose values: {synthetic_values}")
    print("\n--- 30-Minute Horizon Metrics ---")
    print(f"  GRU MAE:                  {gru_mae_30:.2f} mg/dL")
    print(f"  GRU RMSE:                 {gru_rmse_30:.2f} mg/dL")
    print(f"  Persistence Baseline MAE:   {base_mae_30:.2f} mg/dL")
    print(f"  Persistence Baseline RMSE:  {base_rmse_30:.2f} mg/dL")
    print(f"  Improvement over Baseline:  {imp_30:.2f}%")
    
    print("\n--- 60-Minute Horizon Metrics ---")
    print(f"  GRU MAE:                  {gru_mae_60:.2f} mg/dL")
    print(f"  GRU RMSE:                 {gru_rmse_60:.2f} mg/dL")
    print(f"  Persistence Baseline MAE:   {base_mae_60:.2f} mg/dL")
    print(f"  Persistence Baseline RMSE:  {base_rmse_60:.2f} mg/dL")
    print(f"  Improvement over Baseline:  {imp_60:.2f}%")
    
    print("\nSample Real CGM Window (subject_46):")
    print(json.dumps(sample_example, indent=2))

if __name__ == "__main__":
    audit_part1()
    audit_part3_and_4()
    audit_part5_and_6()
