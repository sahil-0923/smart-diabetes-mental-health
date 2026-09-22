import os
import json
import pickle
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import tensorflow as tf

class ForecastModelService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ForecastModelService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, artifacts_dir="ai/artifacts"):
        if getattr(self, "_initialized", False):
            return
        
        self.artifacts_dir = artifacts_dir
        self.model_path = os.path.join(artifacts_dir, "glucose_gru.keras")
        self.scaler_path = os.path.join(artifacts_dir, "scaler.pkl")
        self.meta_path = os.path.join(artifacts_dir, "model_metadata.json")
        
        self.model = None
        self.scaler = None
        self.metadata = {}
        self.is_loaded = False
        
        self.load_artifacts()
        self._initialized = True

    def load_artifacts(self):
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
                self.model = tf.keras.models.load_model(self.model_path)
                with open(self.scaler_path, "rb") as f:
                    self.scaler = pickle.load(f)
                if os.path.exists(self.meta_path):
                    with open(self.meta_path, "r") as f:
                        self.metadata = json.load(f)
                self.is_loaded = True
                print("Glucose GRU Model and Scaler loaded successfully.")
            else:
                self.is_loaded = False
                print("Model artifacts not found on disk yet.")
        except Exception as e:
            print(f"Error loading model artifacts: {e}")
            self.is_loaded = False

    def get_status(self, user_record_count=0):
        return {
            "model_loaded": self.is_loaded,
            "model_version": self.metadata.get("model_version", "N/A"),
            "required_sequence_length": 36,
            "available_user_records": user_record_count,
            "forecast_available": self.is_loaded and user_record_count >= 5
        }

    def prepare_sequence_from_records(self, records):
        """
        Converts user HealthRecord objects into a valid (1, 36, 5) input window.
        Returns numpy array of shape (1, 36, 5) or None if insufficient data.
        """
        if not records or len(records) < 5:
            return None
            
        # Convert records to pandas dataframe
        data = []
        for r in records:
            if getattr(r, "glucose", None) is not None:
                ts = r.date if isinstance(r.date, datetime) else datetime.utcnow()
                data.append({
                    "timestamp": ts,
                    "glucose": float(r.glucose),
                    "steps": float(r.steps or 0),
                    "sleep": float(r.sleep or 7.0),
                    "stress": float(r.stress or 5.0)
                })
                
        if len(data) < 5:
            return None
            
        df = pd.DataFrame(data).sort_values("timestamp")
        
        # Build 36-step trajectory matching the model's 5-minute features
        # The final timestep (i=35) is EXACTLY anchored on the latest valid glucose record
        latest_glucose = float(df["glucose"].iloc[-1])
        latest_steps = float(df["steps"].iloc[-1])
        latest_sleep = float(df["sleep"].iloc[-1])
        
        now = df["timestamp"].iloc[-1]
        timestamps = [now - timedelta(minutes=5*(35 - i)) for i in range(36)]
        
        # Linearly interpolate previous user readings into the 36-step window leading to latest_glucose
        raw_glucoses = df["glucose"].tolist()
        num_raw = len(raw_glucoses)
        
        feature_matrix = []
        for i, ts in enumerate(timestamps):
            hour = ts.hour + ts.minute / 60.0
            h_sin = np.sin(2 * np.pi * hour / 24.0)
            h_cos = np.cos(2 * np.pi * hour / 24.0)
            
            if i == 35:
                # Timestep 35 is strictly the latest valid glucose measurement
                g_val = latest_glucose
            elif num_raw >= 36:
                g_val = float(raw_glucoses[num_raw - 36 + i])
            else:
                # Map available raw readings smoothly across the 36 timesteps leading to latest_glucose
                ratio = i / 35.0
                idx_float = ratio * (num_raw - 1)
                idx_low = int(np.floor(idx_float))
                idx_high = min(num_raw - 1, int(np.ceil(idx_float)))
                weight = idx_float - idx_low
                g_val = float(raw_glucoses[idx_low] * (1.0 - weight) + raw_glucoses[idx_high] * weight)
                
            is_sleeping = 1.0 if (latest_sleep > 0 and (hour >= 23 or hour <= 6.5)) else 0.0
            step_val = latest_steps / 36.0 if not is_sleeping else 0.0
            
            feature_matrix.append([g_val, step_val, is_sleeping, h_sin, h_cos])
            
        return np.array([feature_matrix], dtype=np.float32)

    def predict_forecast(self, records):
        """
        Runs real GRU inference for 30-min and 60-min glucose forecasts.
        """
        if not self.is_loaded:
            self.load_artifacts()
            
        if not self.is_loaded:
            return {
                "available": False,
                "prediction_30min": None,
                "prediction_60min": None,
                "model_version": None,
                "input_records": len(records) if records else 0,
                "message": "GRU model is currently unavailable."
            }
            
        seq = self.prepare_sequence_from_records(records)
        if seq is None:
            return {
                "available": False,
                "prediction_30min": None,
                "prediction_60min": None,
                "model_version": self.metadata.get("model_version", "v1.0.0-gru"),
                "input_records": len(records) if records else 0,
                "message": "More glucose history is required before forecasting is available (minimum 5 readings)."
            }
            
        # Scale input
        num_features = seq.shape[2]
        seq_flat = seq.reshape(-1, num_features)
        seq_scaled = self.scaler.transform(seq_flat).reshape(seq.shape)
        
        # Inference
        preds = self.model.predict(seq_scaled, verbose=0) # Shape: (1, 2)
        pred_30 = float(preds[0, 0])
        pred_60 = float(preds[0, 1])
        
        latest_valid_glucose = float(records[-1].glucose) if records and hasattr(records[-1], 'glucose') and records[-1].glucose is not None else round(float(seq[0, -1, 0]), 1)
        return {
            "available": True,
            "prediction_30min": round(pred_30, 1),
            "prediction_60min": round(pred_60, 1),
            "current_glucose": round(latest_valid_glucose, 1),
            "model_version": self.metadata.get("model_version", "v1.0.0-gru-diatrend"),
            "input_records": len(records),
            "message": "AI forecast generated successfully."
        }

    def simulate_whatif(self, records, exercise_mins=0, sleep_hours=7.0, meal_context="Normal"):
        """
        Runs what-if simulation by modifying sequence inputs and comparing GRU predictions.
        """
        base_pred = self.predict_forecast(records)
        if not base_pred["available"]:
            return {
                "available": False,
                "message": "Insufficient historical data to simulate scenario."
            }
            
        seq = self.prepare_sequence_from_records(records)
        seq_mod = seq.copy()
        
        # Apply hypothetical lifestyle modifications to recent timesteps
        # E.g. exercise increases steps and reduces glucose response
        added_steps = (float(exercise_mins) * 100.0) / 36.0
        seq_mod[0, :, 1] += added_steps
        
        # Sleep adjustment
        if float(sleep_hours) < 6.0:
            seq_mod[0, :, 0] += 5.0 # Sleep deprivation raises glucose response
            
        # Meal context adjustment
        if meal_context == "High Carb":
            seq_mod[0, -6:, 0] += 20.0
        elif meal_context == "Low Carb":
            seq_mod[0, -6:, 0] -= 10.0
            
        num_features = seq_mod.shape[2]
        seq_mod_scaled = self.scaler.transform(seq_mod.reshape(-1, num_features)).reshape(seq_mod.shape)
        
        preds_mod = self.model.predict(seq_mod_scaled, verbose=0)
        sim_30 = float(preds_mod[0, 0])
        sim_60 = float(preds_mod[0, 1])
        
        return {
            "available": True,
            "baseline_30min": base_pred["prediction_30min"],
            "baseline_60min": base_pred["prediction_60min"],
            "simulated_30min": round(sim_30, 1),
            "simulated_60min": round(sim_60, 1),
            "delta_30min": round(sim_30 - base_pred["prediction_30min"], 1),
            "delta_60min": round(sim_60 - base_pred["prediction_60min"], 1),
            "model_version": self.metadata.get("model_version", "v1.0.0-gru")
        }

model_service = ForecastModelService()
