from . import create_dash, create_flask
from .loader import clear_cache

SERVER = create_flask("../config.py")
APP = create_dash(SERVER)
clear_cache()

with SERVER.app_context():
    from . import callbacks
    from .layout import layout

    APP.layout = layout
