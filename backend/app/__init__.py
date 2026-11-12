"""SmartFlow Flask Application Factory.
Configures database, JWT authentication, CORS, error handlers, and core diagnostic routes.
"""
import os
import logging
from flask import Flask, jsonify
from sqlalchemy import text
from backend.config import config_by_name, Config
from backend.app.extensions import db, migrate, jwt, cors

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)
logger = logging.getLogger('smartflow')


def create_app(config_name: str = None) -> Flask:
    """Application factory for SmartFlow backend."""
    if not config_name:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    config_class = config_by_name.get(config_name, Config)
    app.config.from_object(config_class)

    # Database connectivity check & SQLite fallback safeguard
    target_uri = app.config['SQLALCHEMY_DATABASE_URI']
    if target_uri.startswith('mysql') and app.config.get('USE_SQLITE_FALLBACK', True):
        try:
            from sqlalchemy import create_engine
            temp_engine = create_engine(target_uri, pool_pre_ping=True)
            with temp_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Successfully connected to MySQL database engine.")
        except Exception as e:
            logger.warning(
                f"MySQL connection unavailable ({e}). Automatically activating SQLite fallback for development."
            )
            app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{app.config['SQLITE_DATABASE_PATH']}"
            app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {}

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": app.config.get('CORS_ORIGINS', '*')}},
        supports_credentials=True
    )

    # Register Global Health & Diagnostics Route
    @app.route('/api/health', methods=['GET'])
    def health_check():
        db_status = 'connected'
        db_engine = 'unknown'
        try:
            with db.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                db_engine = db.engine.name
        except Exception as ex:
            db_status = f'disconnected ({str(ex)})'

        return jsonify({
            'status': 'healthy',
            'application': 'SmartFlow AI Retail & E-Commerce Management System',
            'version': '1.0.0',
            'database': {
                'status': db_status,
                'engine': db_engine
            }
        }), 200

    # Register JSON error handlers
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 'Bad Request',
            'message': str(error.description if hasattr(error, 'description') else error)
        }), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'success': False,
            'error': 'Unauthorized',
            'message': 'Authentication required or invalid token.'
        }), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'success': False,
            'error': 'Forbidden',
            'message': 'You do not have permission to access this resource.'
        }), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 'Not Found',
            'message': 'The requested API endpoint was not found.'
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred on the server.'
        }), 500

    # JWT Error handlers
    @jwt.unauthorized_loader
    def missing_token_callback(reason):
        return jsonify({
            'success': False,
            'error': 'Authorization Required',
            'message': f'Request does not contain an access token: {reason}'
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(reason):
        return jsonify({
            'success': False,
            'error': 'Invalid Token',
            'message': f'Provided token is invalid: {reason}'
        }), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'success': False,
            'error': 'Token Expired',
            'message': 'The token has expired. Please log in again.'
        }), 401

    # Register Blueprints
    from backend.app.routes.auth_routes import auth_bp
    from backend.app.routes.category_routes import category_bp
    from backend.app.routes.product_routes import product_bp
    from backend.app.routes.inventory_routes import inventory_bp
    from backend.app.routes.store_routes import store_bp
    from backend.app.routes.cart_routes import cart_bp
    from backend.app.routes.coupon_routes import coupon_bp
    from backend.app.routes.order_routes import order_bp
    from backend.app.routes.pos_routes import pos_bp
    from backend.app.routes.transaction_routes import transaction_bp
    from backend.app.routes.customer_routes import customer_bp
    from backend.app.routes.employee_routes import employee_bp
    from backend.app.routes.analytics_routes import analytics_bp
    from backend.app.routes.aiml_routes import aiml_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(store_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(coupon_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(pos_bp)
    app.register_blueprint(transaction_bp)
    app.register_blueprint(customer_bp)
    app.register_blueprint(employee_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(aiml_bp)

    return app
