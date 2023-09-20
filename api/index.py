from flask import Flask
import threading
from dotenv import load_dotenv
import os

load_dotenv()
import worker

app = Flask(__name__)

# Import routes after app is created to avoid circular imports
from routes import *

if __name__ == "__main__":
    # Start the worker thread
    threading.Thread(target=worker.worker).start()
    app.run()
