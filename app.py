import os
from flask import Flask
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('JWT_SECRET')
    app.config['MONGO_URI'] = os.environ.get('MONGO_URI')

    # Register Blueprints
    from controllers.auth_controller import auth_bp
    from controllers.bank_controller import bank_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(bank_bp)

    # Static
    @app.route('/static/<path:filename>')
    def custom_static(filename):
        from flask import send_from_directory
        return send_from_directory('static', filename)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
