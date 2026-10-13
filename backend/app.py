import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from haibo import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=26284, debug=False)
