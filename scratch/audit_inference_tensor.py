import os
import sys
sys.path.insert(0, os.path.abspath("."))
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import pickle
import tensorflow as tf

from app import app, db, User, HealthRecord
from ai.model_service import model_service

def audit_inference_tensor():
    with app.app_context():
        user = User.query.filter_by(name="Rahul Kumar").first()
        if not user:
            print("Rahul Kumar not found!")
            return
            
        records = HealthRecord.query.filter_by(user_id=user.id, is_valid=True).order_by(HealthRecord.date.asc()).all()
        print(f"Patient: {user.name}")
        print(f"Found {len(records)} valid records in database:")
        for idx, r in enumerate(records):
            print(f"  User Record {idx+1}: Timestamp={r.date} | Glucose={r.glucose} mg/dL | Steps={r.steps} | Sleep={r.sleep}h | Stress={r.stress}")

        # Generate tensor using model_service
        seq = model_service.prepare_sequence_from_records(records)
        
        # Load Scaler
        with open(model_service.scaler_path, "rb") as f:
            scaler = pickle.load(f)
            
        num_features = seq.shape[2]
        seq_flat = seq.reshape(-1, num_features)
        seq_scaled = scaler.transform(seq_flat).reshape(seq.shape)
        
        # Predict
        preds = model_service.model.predict(seq_scaled, verbose=0)
        
        print("\n" + "="*90)
        print("EXACT 36 TIMESTEPS GENERATED FOR RAHUL KUMAR (ai/model_service.py)")
        print("="*90)
        print(f"{'Step':<5} | {'Timestamp (5-min grid)':<22} | {'Glucose (mg/dL)':<15} | {'Steps':<8} | {'is_sleeping':<12} | {'hour_sin':<10} | {'hour_cos':<10} | {'Type'}")
        print("-" * 115)
        
        raw_glucoses = [r.glucose for r in records]
        num_raw = len(raw_glucoses)
        
        # Replicate timestamps
        now = records[-1].date
        timestamps = [now - timedelta(minutes=5*(35 - i)) for i in range(36)]
        
        for i in range(36):
            ts_str = timestamps[i].strftime("%Y-%m-%d %H:%M:%S")
            g_val = seq[0, i, 0]
            step_val = seq[0, i, 1]
            sleep_val = seq[0, i, 2]
            h_sin = seq[0, i, 3]
            h_cos = seq[0, i, 4]
            
            # Classification
            if i == 0:
                val_type = f"Anchor 1 (Record 1: {raw_glucoses[0]} mg/dL)"
            elif i == 35:
                val_type = f"Anchor 5 (Record 5: {raw_glucoses[-1]} mg/dL - LATEST)"
            elif i in [round(35.0 / 4 * 1), round(35.0 / 4 * 2), round(35.0 / 4 * 3)]:
                val_type = "Interpolation Node (Anchor matching intermediate record)"
            else:
                val_type = "Linear Interpolation between daily check-in nodes"
                
            print(f"{i+1:<5} | {ts_str:<22} | {g_val:<15.2f} | {step_val:<8.2f} | {sleep_val:<12.1f} | {h_sin:<10.4f} | {h_cos:<10.4f} | {val_type}")
            
        print("\n" + "="*90)
        print("SCALER & MODEL INFERENCE VERIFICATION")
        print("="*90)
        print(f"1. Input Tensor Shape: {seq.shape} -> (Batch Size=1, Sequence Length=36, Features=5)")
        print(f"2. Scaler Means: {scaler.mean_}")
        print(f"3. Scaler Scales: {scaler.scale_}")
        print(f"4. Scaled Tensor Sample (Step 36): {seq_scaled[0, -1, :]}")
        print(f"5. Final Timestep Glucose: {seq[0, -1, 0]:.1f} mg/dL (Expected latest: 132.0 mg/dL)")
        print(f"6. Raw Model Predictions (preds shape: {preds.shape}):")
        print(f"   • Horizon 1 (+30 min): {preds[0, 0]:.2f} mg/dL -> Rounded: {round(float(preds[0, 0]), 1)} mg/dL")
        print(f"   • Horizon 2 (+60 min): {preds[0, 1]:.2f} mg/dL -> Rounded: {round(float(preds[0, 1]), 1)} mg/dL")

if __name__ == "__main__":
    audit_inference_tensor()
