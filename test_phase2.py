import os
import unittest
from datetime import datetime, timedelta
import numpy as np

from app import app, db, User, HealthRecord
from ai.model_service import model_service

class TestPhase2GRU(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        cls.client = app.test_client()

    def setUp(self):
        with app.app_context():
            db.session.rollback()
            db.session.remove()

    def tearDown(self):
        with app.app_context():
            db.session.rollback()
            db.session.remove()

    def test_01_artifacts_exist(self):
        """Verify model artifacts and metadata files exist."""
        self.assertTrue(os.path.exists("ai/artifacts/scaler.pkl"), "scaler.pkl missing")
        self.assertTrue(os.path.exists("ai/artifacts/glucose_gru.keras"), "glucose_gru.keras missing")
        self.assertTrue(os.path.exists("ai/artifacts/model_metadata.json"), "model_metadata.json missing")
        self.assertTrue(os.path.exists("docs/MODEL_REPORT.md"), "MODEL_REPORT.md missing")

    def test_02_model_service_loading(self):
        """Verify model_service loads artifacts successfully."""
        model_service.load_artifacts()
        self.assertTrue(model_service.is_loaded, "Model service should be loaded")
        self.assertIsNotNone(model_service.model, "Model should not be None")
        self.assertIsNotNone(model_service.scaler, "Scaler should not be None")

    def test_03_prediction_insufficient_history(self):
        """Verify user with < 5 readings receives available=False and no fake numbers."""
        with app.app_context():
            # Find or create user
            u_id = 99881
            user = db.session.get(User, u_id)
            if not user:
                user = User(id=u_id, name="Test Insufficient", email="test_insufficient_99881@test.com", password="pw", profile_completed=True, onboarding_completed=True)
                db.session.add(user)
                db.session.commit()

            # Clear old records
            HealthRecord.query.filter_by(user_id=u_id).delete()
            for i in range(2):
                hr = HealthRecord(user_id=u_id, date=datetime.utcnow() - timedelta(days=i), glucose=120.0 + i*5)
                db.session.add(hr)
            db.session.commit()
            
            records = HealthRecord.query.filter_by(user_id=u_id).order_by(HealthRecord.date.asc()).all()
            res = model_service.predict_forecast(records)
            
            self.assertFalse(res["available"])
            self.assertIsNone(res["prediction_30min"])
            self.assertIsNone(res["prediction_60min"])
            self.assertIn("More glucose history is required", res["message"])

    def test_04_prediction_sufficient_history(self):
        """Verify user with >= 5 readings receives real continuous GRU forecasts."""
        with app.app_context():
            u_id = 99882
            user = db.session.get(User, u_id)
            if not user:
                user = User(id=u_id, name="Test Sufficient", email="test_sufficient_99882@test.com", password="pw", profile_completed=True, onboarding_completed=True)
                db.session.add(user)
                db.session.commit()

            HealthRecord.query.filter_by(user_id=u_id).delete()
            base_g = 130.0
            for i in range(7):
                hr = HealthRecord(
                    user_id=u_id,
                    date=datetime.utcnow() - timedelta(days=7-i),
                    glucose=base_g + i*3.0,
                    steps=5000,
                    sleep=7.5,
                    stress=4.0
                )
                db.session.add(hr)
            db.session.commit()
            
            records = HealthRecord.query.filter_by(user_id=u_id).order_by(HealthRecord.date.asc()).all()
            res = model_service.predict_forecast(records)
            
            self.assertTrue(res["available"])
            self.assertIsNotNone(res["prediction_30min"])
            self.assertIsNotNone(res["prediction_60min"])
            self.assertIsInstance(res["prediction_30min"], float)
            self.assertIsInstance(res["prediction_60min"], float)
            self.assertGreater(res["prediction_30min"], 40.0)
            self.assertLess(res["prediction_30min"], 400.0)

    def test_05_whatif_simulation(self):
        """Verify What-If scenario simulation returns delta comparisons."""
        with app.app_context():
            u_id = 99882
            records = HealthRecord.query.filter_by(user_id=u_id).order_by(HealthRecord.date.asc()).all()
            
            res = model_service.simulate_whatif(records, exercise_mins=45, sleep_hours=8.0, meal_context="Low Carb")
            self.assertTrue(res["available"])
            self.assertIn("baseline_30min", res)
            self.assertIn("simulated_30min", res)
            self.assertIn("delta_30min", res)
            self.assertIn("delta_60min", res)

    def test_06_user_isolation(self):
        """Verify User A's history cannot leak into User B's forecasting pipeline."""
        with app.app_context():
            u_id_a = 99883
            u_id_b = 99884
            
            user_a = db.session.get(User, u_id_a)
            if not user_a:
                user_a = User(id=u_id_a, name="Iso A", email="iso_a_99883@test.com", password="pw", profile_completed=True, onboarding_completed=True)
                db.session.add(user_a)
                
            user_b = db.session.get(User, u_id_b)
            if not user_b:
                user_b = User(id=u_id_b, name="Iso B", email="iso_b_99884@test.com", password="pw", profile_completed=True, onboarding_completed=True)
                db.session.add(user_b)
                
            db.session.commit()

            HealthRecord.query.filter_by(user_id=u_id_a).delete()
            HealthRecord.query.filter_by(user_id=u_id_b).delete()
            
            for i in range(6):
                hr = HealthRecord(user_id=u_id_a, date=datetime.utcnow() - timedelta(days=6-i), glucose=140.0)
                db.session.add(hr)
            db.session.commit()
            
            records_a = HealthRecord.query.filter_by(user_id=u_id_a).order_by(HealthRecord.date.asc()).all()
            records_b = HealthRecord.query.filter_by(user_id=u_id_b).order_by(HealthRecord.date.asc()).all()
            
            res_a = model_service.predict_forecast(records_a)
            res_b = model_service.predict_forecast(records_b)
            
            self.assertTrue(res_a["available"])
            self.assertFalse(res_b["available"])

if __name__ == "__main__":
    unittest.main()
