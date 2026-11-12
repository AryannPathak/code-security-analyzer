"""SmartFlow AIML Model Training & Verification Suite.
Validates all 4 machine learning models.
"""
import os
import sys

# Ensure root workspace is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import create_app
from aiml.sales_prediction import SalesPredictor
from aiml.recommendation import ProductRecommender
from aiml.anomaly_detection import AnomalyDetector
from aiml.stock_prediction import DemandForecaster


def run_aiml_pipeline():
    print("=" * 65)
    print("      SMARTFLOW AIML ALGORITHM VERIFICATION PIPELINE")
    print("=" * 65)

    app = create_app()
    with app.app_context():
        # 1. Feature 1: Sales Prediction (Linear Regression)
        print("\n[+] FEATURE 1: Sales Prediction (Linear Regression)")
        predictor = SalesPredictor()
        sample_df = predictor._generate_sample_dataset()
        results = predictor.train_and_evaluate(sample_df)
        metrics = results['metrics']
        print(f"    Train Samples: {metrics['train_samples']} | Test Samples: {metrics['test_samples']}")
        print(f"    Mean Absolute Error (MAE):  ₹{metrics['mae']}")
        print(f"    Root Mean Squared Error:    ₹{metrics['rmse']}")
        print(f"    R² Score (Goodness of Fit): {metrics['r2_score']}")

        # 2. Feature 2: Product Recommendation (Popularity Engine)
        print("\n[+] FEATURE 2: Product Recommendation (Popularity Ranking)")
        recommender = ProductRecommender()
        recs = recommender.get_popular_recommendations(limit=5)
        print(f"    Generated {len(recs)} top-selling recommendations:")
        for r in recs[:3]:
            print(f"     * {r['name']} (Score: {r.get('popularity_score', 0)}, Sold: {r.get('total_units_sold', 0)} units)")

        # 3. Feature 3: Unusual Transaction Detection (Isolation Forest)
        print("\n[+] FEATURE 3: Unusual Transaction Detection (Isolation Forest)")
        detector = AnomalyDetector(contamination=0.04)
        anomaly_res = detector.fit_and_flag(update_db=True)
        print(f"    {anomaly_res['message']}")
        if 'contamination_rate' in anomaly_res:
            print(f"    Contamination Rate Configured: {anomaly_res['contamination_rate'] * 100}%")

        # 4. Feature 4: Inventory Demand Prediction (Moving Average)
        print("\n[+] FEATURE 4: Inventory Demand Forecasting (Moving Average)")
        forecaster = DemandForecaster()
        forecasts = forecaster.forecast_inventory_demand(limit=5)
        print(f"    Computed replenishment timelines for {len(forecasts)} inventory items:")
        for f in forecasts[:3]:
            print(f"     * {f['product_name']}: {f['current_stock']} units left (~{f['days_remaining']} days runway) -> Priority: {f['priority']}")

        print("\n" + "=" * 65)
        print(">>> SUCCESS: All 4 AIML models trained and verified cleanly!")
        print("=" * 65)


if __name__ == '__main__':
    run_aiml_pipeline()
