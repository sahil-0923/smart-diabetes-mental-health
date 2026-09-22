import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_diatrend_dataset(base_dir="data/longitudinal/DiaTrend", num_subjects=54, days_per_subject=14):
    os.makedirs(base_dir, exist_ok=True)
    np.random.seed(42)
    
    demographics = []
    
    print(f"Generating realistic DiaTrend dataset with {num_subjects} subjects in {base_dir}...")
    
    start_base_date = datetime(2025, 1, 1, 0, 0, 0)
    
    for sub_idx in range(1, num_subjects + 1):
        sub_id = f"subject_{sub_idx:02d}"
        sub_folder = os.path.join(base_dir, sub_id)
        os.makedirs(sub_folder, exist_ok=True)
        
        # Demographics
        age = np.random.randint(18, 70)
        gender = np.random.choice(["Male", "Female"])
        diabetes_type = np.random.choice(["Type 1", "Type 2"], p=[0.85, 0.15])
        hba1c = round(np.random.uniform(6.0, 9.5), 1)
        demographics.append({
            "subject_id": sub_id,
            "age": age,
            "gender": gender,
            "diabetes_type": diabetes_type,
            "hba1c": hba1c
        })
        
        # Timeline: 5-minute intervals for days_per_subject
        num_intervals = days_per_subject * 24 * 12 # 288 per day
        timestamps = [start_base_date + timedelta(minutes=5*i) for i in range(num_intervals)]
        
        # Base glucose with diurnal rhythm + random walk + meal excursions
        base_glucose = np.random.uniform(110, 160)
        glucose_vals = []
        curr_g = base_glucose
        
        cgm_records = []
        steps_records = []
        hr_records = []
        
        for ts in timestamps:
            hour = ts.hour + ts.minute / 60.0
            
            # Diurnal baseline variation
            diurnal = 10 * np.sin((hour - 6) * np.pi / 12)
            
            # Meal spikes at ~8am, ~1pm, ~7pm
            meal_spike = 0
            if (7.5 <= hour <= 9.0) or (12.5 <= hour <= 14.0) or (18.5 <= hour <= 20.5):
                if np.random.rand() < 0.7:
                    meal_spike = np.random.uniform(15, 45)
            
            # Steps / Activity
            is_sleeping = 1 if (hour >= 23 or hour <= 6.5) else 0
            if is_sleeping:
                steps = 0
                hr = int(np.random.normal(60, 4))
            else:
                steps = int(max(0, np.random.exponential(15) if np.random.rand() < 0.4 else 0))
                hr = int(np.random.normal(78 + (steps / 10), 8))
            
            # Exercise effect on glucose (drops slightly)
            exercise_effect = -0.05 * steps if steps > 50 else 0
            
            # Stepwise glucose update with mean reversion
            noise = np.random.normal(0, 2.5)
            curr_g = curr_g + 0.1 * (base_glucose + diurnal + meal_spike - curr_g) + noise + exercise_effect
            curr_g = float(np.clip(curr_g, 55.0, 380.0))
            
            # Occasionally missing values (realistic CGM sensor dropouts < 1%)
            if np.random.rand() > 0.005:
                cgm_records.append({"timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"), "glucose": round(curr_g, 1)})
            
            steps_records.append({"timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"), "steps": steps})
            hr_records.append({"timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"), "heart_rate": hr})
        
        # Sleep epochs
        sleep_records = []
        for day in range(days_per_subject):
            sleep_start = start_base_date + timedelta(days=day, hours=23) + timedelta(minutes=int(np.random.normal(0, 20)))
            sleep_end = start_base_date + timedelta(days=day+1, hours=6, minutes=30) + timedelta(minutes=int(np.random.normal(0, 30)))
            sleep_records.append({
                "start_time": sleep_start.strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": sleep_end.strftime("%Y-%m-%d %H:%M:%S"),
                "quality": np.random.choice(["Good", "Restless", "Fair"])
            })
            
        pd.DataFrame(cgm_records).to_csv(os.path.join(sub_folder, "cgm.csv"), index=False)
        pd.DataFrame(steps_records).to_csv(os.path.join(sub_folder, "steps.csv"), index=False)
        pd.DataFrame(hr_records).to_csv(os.path.join(sub_folder, "heart_rate.csv"), index=False)
        pd.DataFrame(sleep_records).to_csv(os.path.join(sub_folder, "sleep.csv"), index=False)
    
    pd.DataFrame(demographics).to_csv(os.path.join(base_dir, "demographics.csv"), index=False)
    print("DiaTrend dataset created successfully!")

if __name__ == "__main__":
    generate_diatrend_dataset()
