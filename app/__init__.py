import config
import warnings
from flask import Flask
from flask.sessions import SecureCookieSessionInterface


def check_session_size(app):
    original_save_session = SecureCookieSessionInterface.save_session

    def custom_save_session(self, app, session, response):
        try:
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                original_save_session(self, app, session, response)

                for warning in w:
                    if issubclass(warning.category, UserWarning) and "The 'session' cookie is too large" in str(
                            warning.message):
                        # Handle the warning
                        print("Session cookie is too large. Clearing session.")
                        session.clear()
                        # You might want to set a flash message or log this event

                        # Re-save the session after clearing
                        original_save_session(self, app, session, response)
        except Exception as e:
            print(f"Error handling session size: {e}")

    SecureCookieSessionInterface.save_session = custom_save_session


def create_app():
    app = Flask(__name__)
    check_session_size(app)

    app.secret_key = config.Config.SECRET_KEY
    with app.app_context():
        from . import routes

    return app
