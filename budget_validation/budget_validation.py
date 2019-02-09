from . import create_dash, create_flask

server = create_flask("../config.py")
app = create_dash(server)

with server.app_context():
    from . import callbacks
    from .layout import layout
    app.layout = layout
