from . import create_dash, create_flask

SERVER = create_flask("../config.py")
APP = create_dash(SERVER)

with SERVER.app_context():
    from . import callbacks
    from .layout import layout

    APP.layout = layout
