from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_user import UserManager

from .config import default

# init SQLAlchemy
db = SQLAlchemy()

def create_app():
    ''' Create a Flask app, configure it. register some project blueprints as 'auth' or 'main', 
        initialize related services as MQTT or SQLAlchemy (with data insertion) and the flask login manager.

        Returns:
            app (object): Configured Flask app

    '''
    # Create Flask app 
    app = Flask(__name__, instance_relative_config=True)

    # Configure the application with the config file
    app.config.from_object(default)

    # Register project blueprints 

    # -> Auth routes
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # -> Non-auth routes 
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # -> Legitimate routes 
    from .legitimate_person import legitimate_person as legitimate_person_blueprint
    app.register_blueprint(legitimate_person_blueprint)

    # -> Historic routes 
    from .historic import historic as historic_blueprint
    app.register_blueprint(historic_blueprint)

    # -> Door routes 
    from .door import door as door_blueprint
    app.register_blueprint(door_blueprint)

    # -> Location routes 
    from .location import location as location_blueprint
    app.register_blueprint(location_blueprint)

    # Import models to create the tables
    from .models import User, Role

    # Init the Flask-User Manager service 
    user_manager = UserManager(app, db, User)

    # Init the SQLAlchemy - DB service
    db.init_app(app)

    # Create the tables with the application context
    with app.app_context():
        db.create_all()
        # If there are no users and no roles create and insert them on the db
        if not User.query.limit(1).all() and not Role.query.limit(1).all():
            from .utils.insert_data_to_db import insert_user_data
            insert_user_data(db)

    # Create the LoginManager
    login_manager = LoginManager()

    # Set the login manager main view as the login service
    login_manager.login_view = 'auth.login'

    # Init the LoginManager service
    login_manager.init_app(app)

    # Define the user loader for the LoginManager
    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        try:
            return User.query.get(int(user_id))
        except:
            return None

    return app
