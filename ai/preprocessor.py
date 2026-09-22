import os
import glob
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

class DiaTrendPreprocessor:
    """
    Preprocessor for the DiaTrend longitudinal multimodal dataset.
    Aligns CGM, steps, and sleep onto a strict 5-minute grid,
    generates temporal cyclic features, and constructs time-series sequences.
    """
    
    def __init__(self, sequence_length=36, horizon_30=6, horizon_60=12):
        self.sequence_length = sequence_length
        self.horizon_30 = horizon_30 # 6 * 5 min = 30 min
        self.horizon_60 = horizon_60 # 12 * 5 min = 60 min
        self.feature_names = ["glucose", "steps", "is_sleeping", "hour_sin", "hour_cos"]

    def load_subject_data(self, subject_dir):
        """
        Loads and aligns CGM, steps, and sleep for a single subject into a 5-minute grid.
        """
        cgm_file = os.path.join(subject_dir, "cgm.csv")
        steps_file = os.path.join(subject_dir, "steps.csv")
        sleep_file = os.path.join(subject_dir, "sleep.csv")
        
        if not os.path.exists(cgm_file):
            return None

        # 1. Load CGM
        df_cgm = pd.read_csv(cgm_file)
        df_cgm['timestamp'] = pd.to_datetime(df_cgm['timestamp'])
        df_cgm = df_cgm.sort_values('timestamp').drop_duplicates('timestamp')
        df_cgm.set_index('timestamp', inplace=True)
        
        # 2. Resample to 5-minute grid
        min_time = df_cgm.index.min().floor('5min')
        max_time = df_cgm.index.max().ceil('5min')
        grid = pd.date_range(start=min_time, end=max_time, freq='5min')
        
        df_grid = pd.DataFrame(index=grid)
        df_grid = df_grid.join(df_cgm[['glucose']])
        
        # Interpolate short gaps (up to 15 min / 3 periods), leave larger gaps as NaN
        df_grid['glucose'] = df_grid['glucose'].interpolate(method='time', limit=3)
        
        # 3. Load and aggregate steps
        if os.path.exists(steps_file):
            df_steps = pd.read_csv(steps_file)
            df_steps['timestamp'] = pd.to_datetime(df_steps['timestamp'])
            df_steps = df_steps.sort_values('timestamp')
            df_steps.set_index('timestamp', inplace=True)
            # Resample sum to 5-min
            df_steps_5m = df_steps.resample('5min').sum()
            df_grid = df_grid.join(df_steps_5m[['steps']])
            df_grid['steps'] = df_grid['steps'].fillna(0)
        else:
            df_grid['steps'] = 0.0

        # 4. Load sleep intervals
        df_grid['is_sleeping'] = 0
        if os.path.exists(sleep_file):
            df_sleep = pd.read_csv(sleep_file)
            for _, row in df_sleep.iterrows():
                s_start = pd.to_datetime(row['start_time'])
                s_end = pd.to_datetime(row['end_time'])
                mask = (df_grid.index >= s_start) & (df_grid.index <= s_end)
                df_grid.loc[mask, 'is_sleeping'] = 1

        # 5. Temporal cyclic features
        hours = df_grid.index.hour + df_grid.index.minute / 60.0
        df_grid['hour_sin'] = np.sin(2 * np.pi * hours / 24.0)
        df_grid['hour_cos'] = np.cos(2 * np.pi * hours / 24.0)
        
        df_grid.reset_index(inplace=True)
        df_grid.rename(columns={'index': 'timestamp'}, inplace=True)
        
        return df_grid

    def create_sequences_for_subject(self, df_subject):
        """
        Creates sliding window sequences from a subject's aligned dataframe.
        X shape: (N, 36, 5)
        y shape: (N, 2) [y_30, y_60]
        """
        if df_subject is None or len(df_subject) < (self.sequence_length + self.horizon_60):
            return np.empty((0, self.sequence_length, len(self.feature_names))), np.empty((0, 2))
        
        values = df_subject[self.feature_names].values
        glucose_idx = self.feature_names.index("glucose")
        
        X_list = []
        y_list = []
        
        total_steps = len(df_subject)
        max_idx = total_steps - self.horizon_60
        
        for i in range(self.sequence_length, max_idx + 1):
            window = values[i - self.sequence_length : i]
            
            # If there are NaNs in input window, skip
            if np.isnan(window).any():
                continue
                
            target_30 = values[i + self.horizon_30 - 1, glucose_idx]
            target_60 = values[i + self.horizon_60 - 1, glucose_idx]
            
            if np.isnan(target_30) or np.isnan(target_60):
                continue
                
            X_list.append(window)
            y_list.append([target_30, target_60])
            
        if not X_list:
            return np.empty((0, self.sequence_length, len(self.feature_names))), np.empty((0, 2))
            
        return np.array(X_list, dtype=np.float32), np.array(y_list, dtype=np.float32)

    def load_all_subjects(self, base_dir="data/longitudinal/DiaTrend"):
        """
        Loads all subjects from DiaTrend and splits deterministically by subject.
        """
        subject_dirs = sorted(glob.glob(os.path.join(base_dir, "subject_*")))
        subject_ids = [os.path.basename(d) for d in subject_dirs]
        
        # Deterministic split: 70% train (38), 15% val (8), 15% test (8)
        n_train = int(len(subject_ids) * 0.70)
        n_val = int(len(subject_ids) * 0.15)
        
        train_subs = subject_ids[:n_train]
        val_subs = subject_ids[n_train : n_train + n_val]
        test_subs = subject_ids[n_train + n_val :]
        
        def process_split(subs):
            X_all, y_all = [], []
            for s_id in subs:
                s_dir = os.path.join(base_dir, s_id)
                df_s = self.load_subject_data(s_dir)
                X_s, y_s = self.create_sequences_for_subject(df_s)
                if len(X_s) > 0:
                    X_all.append(X_s)
                    y_all.append(y_s)
            if X_all:
                return np.vstack(X_all), np.vstack(y_all)
            return np.empty((0, self.sequence_length, len(self.feature_names))), np.empty((0, 2))

        print(f"Loading DiaTrend dataset: Train={len(train_subs)}, Val={len(val_subs)}, Test={len(test_subs)} subjects...")
        X_train, y_train = process_split(train_subs)
        X_val, y_val = process_split(val_subs)
        X_test, y_test = process_split(test_subs)
        
        split_info = {
            "train_subjects": train_subs,
            "val_subjects": val_subs,
            "test_subjects": test_subs
        }
        
        return (X_train, y_train), (X_val, y_val), (X_test, y_test), split_info
