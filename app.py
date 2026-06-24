from flask import Flask, render_template, session 
from config import config

# Import blueprints
from blueprints.auth import auth_bp
from blueprints.training import training_bp

def create_app(config_name='Config'):
    """
      creates and configures the Flask app
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])

    # Register Blueprints 
    app.register_blueprint(auth_bp)
    app.register_blueprint(training_bp)
    
    # Home routes
    @app.route('/')
    @app.route('/home')
    def home():
        return render_template('index.html',user=session.get('user'),show_form=(session.get('user') is None))
    # Training routes
    @app.route('/training')
    def training():
        if 'user' not in session:
            return render_template('index.html',show_form=True,error='Please enter your handle')
        return render_template('training.html',user=session.get('user'),show_form=False)
    return app

# Create app instance
app = create_app('Config')

if __name__ == "__main__":
    app.run(debug=True)