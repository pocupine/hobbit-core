"""
    flask_hobbit
    ~~~~~~~~~~~~

    Common utils for flask app.
"""

from flask import Flask


class HobbitManager:

    def __init__(self, app=None, **kwargs):
        """
        app: The Flask application instance.
        """
        self.app = app
        if app is not None:
            self.init_app(app, **kwargs)

    def init_app(self, app, **kwargs):
        if not isinstance(app, Flask):
            raise TypeError(
                'flask_hobbit.HobbitManager.init_app(): '
                'Parameter "app" is an instance of class "{}" '
                'instead of a subclass of class "flask.Flask".'.format(
                    app.__class__.__name__))

        # Bind Flask-Hobbit to app
        app.hobbit_manager = self
