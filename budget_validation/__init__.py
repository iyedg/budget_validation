from flask import Flask
from dash import Dash
from .utils import get_dash_args_from_flask_config


def create_flask(filename):
    """Create a flask instance
    
    Arguments:
        filename {string} -- the filename of the config. This can either be an
                             absolute filename or a filename relative to the root path.
    
    Returns:
        server -- A flask instance configured from the provided filename
    """

    server = Flask(__package__)
    server.config.from_pyfile(filename)
    return server


def create_dash(server):
    """Create a Dash instance
    
    Arguments:
        server {Flask} -- a flask instance
    """
    app = Dash(
        server=server,
        suppress_callback_exceptions=True,
        **get_dash_args_from_flask_config(server.config),
    )
    server.config.setdefault("TITLE", "Dash")
    app.css.append_css({"external_url": "https://codepen.io/iyedg/pen/gqRLLM.css"})
    app.scripts.config.serve_locally = True
    return app
