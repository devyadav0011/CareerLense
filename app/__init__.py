import os
from flask import Flask, jsonify, render_template
from .config import Config
from .models import db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize database
    db.init_app(app)

    # Ensure uploads folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Register blueprints
    from .routes import (
        main_bp, resume_bp, builder_bp, job_match_bp, ai_bp, export_bp, auth_bp
    )
    app.register_blueprint(main_bp)
    app.register_blueprint(resume_bp)
    app.register_blueprint(builder_bp)
    app.register_blueprint(job_match_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(auth_bp)

    # Context processors for global templates
    @app.context_processor
    def inject_global_data():
        return {
            'app_name': 'CareerLense',
            'tagline': 'See Your Career Clearly.',
            'secondary_tagline': 'Build. Analyze. Improve.',
            'no_login_badge': 'No Login Required'
        }

    # Custom Error Handlers (Never expose stack traces, user-friendly messages)
    @app.errorhandler(400)
    def bad_request(error):
        if app.debug:
            pass
        return jsonify({
            'error': 'Bad Request',
            'message': getattr(error, 'description', 'Invalid request data provided.')
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        if getattr(error, 'description', None) and 'api' in str(error):
            return jsonify({'error': 'Resource not found.'}), 404
        return render_template('base.html', not_found=True), 404

    @app.errorhandler(413)
    def request_entity_too_large(error):
        return jsonify({
            'error': 'File Too Large',
            'message': f'Uploaded file exceeds the maximum allowed size of {app.config["MAX_UPLOAD_SIZE_MB"]}MB. Please choose a smaller file.'
        }), 413

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'CareerLense encountered an unexpected error processing your request. Please try again.'
        }), 500

    # Create tables on startup
    with app.app_context():
        db.create_all()

    return app
