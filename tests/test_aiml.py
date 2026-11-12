"""AIML Algorithms and Predictive Endpoints Test Suite."""
import pytest
from datetime import datetime, timezone, timedelta
from aiml.sales_prediction import SalesPredictor
from aiml.recommendation import ProductRecommender
from aiml.anomaly_detection import AnomalyDetector
from aiml.stock_prediction import DemandForecaster


def test_linear_regression_sales_prediction():
    """Verify Feature 1: Linear Regression model calculates MAE, RMSE, and R2."""
    predictor = SalesPredictor()
    sample_data = predictor._generate_sample_dataset()
    assert len(sample_data) >= 30

    eval_result = predictor.train_and_evaluate(sample_data)
    assert 'metrics' in eval_result
    metrics = eval_result['metrics']
    assert 'mae' in metrics and metrics['mae'] >= 0
    assert 'rmse' in metrics and metrics['rmse'] >= 0
    assert 'r2_score' in metrics
    assert 'train_samples' in metrics and metrics['train_samples'] > 0

    # Test future forecast
    forecast = predictor.predict_future(
        last_date=datetime.now(timezone.utc),
        days_ahead=7,
        start_trend_idx=len(sample_data)
    )
    assert len(forecast) == 7
    for day in forecast:
        assert 'date' in day
        assert 'predicted_sales' in day
        assert day['predicted_sales'] > 0


def test_popularity_product_recommender(app, sample_data):
    """Verify Feature 2: Popularity-based recommendation algorithm."""
    with app.app_context():
        recommender = ProductRecommender()
        recs = recommender.get_popular_recommendations(limit=5)
        assert isinstance(recs, list)
        for item in recs:
            assert 'id' in item
            assert 'name' in item
            assert 'price' in item


def test_isolation_forest_anomaly_detection(app):
    """Verify Feature 3: Isolation Forest detects transaction outliers."""
    detector = AnomalyDetector(contamination=0.1)

    # Synthetic transaction values with extreme outliers
    normal_amounts = [200.0, 350.0, 500.0, 420.0, 600.0, 150.0, 800.0, 300.0] * 5
    outlier_amounts = [85000.0, 99999.0]
    all_amounts = normal_amounts + outlier_amounts

    labels, scores = detector.fit_predict(all_amounts)
    assert len(labels) == len(all_amounts)
    assert len(scores) == len(all_amounts)

    # Verify outlier flagged (-1)
    flagged_indices = [i for i, lbl in enumerate(labels) if lbl == -1]
    assert len(flagged_indices) > 0


def test_demand_forecasting_moving_average(app, sample_data):
    """Verify Feature 4: Blended 7-day and 30-day Moving Average."""
    with app.app_context():
        forecaster = DemandForecaster()
        results = forecaster.forecast_inventory_demand(store_id=sample_data['store_id'], limit=10)
        assert isinstance(results, list)
        if len(results) > 0:
            item = results[0]
            assert 'current_stock' in item
            assert 'daily_demand_rate' in item
            assert 'days_remaining' in item
            assert 'priority' in item


def test_api_predict_sales_endpoint(client, sample_data, employee_headers):
    """Test REST API endpoint for sales predictions."""
    response = client.get('/api/ai/predict-sales?days_ahead=7', headers=employee_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'metrics' in data
    assert 'future_forecast' in data
    assert len(data['future_forecast']) == 7


def test_api_recommendations_endpoint(client, sample_data):
    """Test public REST API endpoint for product recommendations."""
    response = client.get('/api/ai/recommendations?limit=4')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'recommendations' in data


def test_api_anomalies_endpoint(client, sample_data, admin_headers):
    """Test Admin REST API endpoint for flagged transaction anomalies."""
    response = client.get('/api/ai/anomalies', headers=admin_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'anomalies' in data


def test_api_inventory_forecast_endpoint(client, sample_data, employee_headers):
    """Test Staff REST API endpoint for inventory demand runway."""
    response = client.get(f"/api/ai/inventory-forecast?store_id={sample_data['store_id']}", headers=employee_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'forecasts' in data
