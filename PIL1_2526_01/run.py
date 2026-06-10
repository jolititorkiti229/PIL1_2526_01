import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend import create_app, socketio
from backend.routes import messages as msg_events  # noqa: F401

app = create_app()

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
