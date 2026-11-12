"""AIML Model Serving REST API routes for SmartFlow."""
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from sqlalchemy import func
from backend.app.extensions import db
from backend.app.models.order import Transaction
from backend.app.auth.decorators import employee_required, admin_required
from aiml.sales_prediction import SalesPredictor
from aiml.recommendation import ProductRecommender
from aiml.anomaly_detection import AnomalyDetector
from aiml.stock_prediction import DemandForecaster

aiml_bp = Blueprint('aiml', __name__, url_prefix='/api/ai')


@aiml_bp.route('/predict-sales', methods=['GET'])
@employee_required()
def predict_sales():
    """FEATURE 1: Sales Prediction using Linear Regression."""
    days_ahead = request.args.get('days_ahead', 7, type=int)

    # 1. Fetch historical daily sales from transactions
    txns = db.session.query(
        func.date(Transaction.created_at).label('date'),
        func.sum(Transaction.amount).label('amount')
    ).filter(Transaction.status == 'SUCCESS')\
     .group_by(func.date(Transaction.created_at))\
     .order_by(func.date(Transaction.created_at).asc())\
     .all()

    daily_records = [{'date': str(t[0]), 'amount': float(t[1])} for t in txns]
    predictor = SalesPredictor()

    if len(daily_records) < 7:
        daily_records = predictor._generate_sample_dataset()

    evaluation = predictor.train_and_evaluate(daily_records)

    last_date_str = str(daily_records[-1]['date'])[:10]
    last_date = datetime.strptime(last_date_str, "%Y-%m-%d")

    future_forecast = predictor.predict_future(
        last_date=last_date,
        days_ahead=min(days_ahead, 30),
        start_trend_idx=len(daily_records)
    )

    return jsonify({
        'success': True,
        'algorithm': 'Linear Regression (Ordinary Least Squares)',
        'objective': 'Predict future daily retail sales based on calendar & trend features',
        'metrics': evaluation['metrics'],
        'history_comparison': evaluation['history_comparison'],
        'future_forecast': future_forecast
    }), 200


@aiml_bp.route('/recommendations', methods=['GET'])
def get_recommendations():
    """FEATURE 2: Product Recommendations (Popularity & Frequency)."""
    category_id = request.args.get('category_id', type=int)
    limit = request.args.get('limit', 8, type=int)

    recommender = ProductRecommender()
    recommendations = recommender.get_popular_recommendations(
        category_id=category_id,
        limit=min(limit, 24)
    )

    return jsonify({
        'success': True,
        'algorithm': 'Popularity-Based Collaborative Frequency Ranking',
        'count': len(recommendations),
        'recommendations': recommendations
    }), 200


@aiml_bp.route('/anomalies', methods=['GET'])
@admin_required()
def get_anomalies():
    """FEATURE 3: View flagged unusual transactions for Admin Review."""
    flagged_txns = Transaction.query.filter_by(is_flagged_anomaly=True)\
                                    .order_by(Transaction.anomaly_score.asc())\
                                    .limit(50)\
                                    .all()

    return jsonify({
        'success': True,
        'count': len(flagged_txns),
        'anomalies': [t.to_dict() for t in flagged_txns]
    }), 200


@aiml_bp.route('/anomalies/run-detection', methods=['POST'])
@admin_required()
def run_anomaly_detection():
    """FEATURE 3: Trigger fresh Isolation Forest scan on transaction ledger."""
    contamination = request.args.get('contamination', 0.03, type=float)
    detector = AnomalyDetector(contamination=contamination)
    results = detector.fit_and_flag(update_db=True)

    return jsonify({
        'success': True,
        'algorithm': 'Isolation Forest (scikit-learn)',
        'results': results
    }), 200


@aiml_bp.route('/inventory-forecast', methods=['GET'])
@employee_required()
def get_inventory_forecast():
    """FEATURE 4: Inventory Demand Forecasting using Moving Average."""
    store_id = request.args.get('store_id', type=int)
    limit = request.args.get('limit', 50, type=int)

    forecaster = DemandForecaster()
    forecasts = forecaster.forecast_inventory_demand(store_id=store_id, limit=limit)

    return jsonify({
        'success': True,
        'algorithm': 'Moving Average (7-Day & 30-Day Window Blended)',
        'count': len(forecasts),
        'forecasts': forecasts
    }), 200
